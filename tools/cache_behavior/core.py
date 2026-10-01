import time

import numpy as np
import torch
from transformers import DynamicCache


def sync(device):
    device = torch.device(device)
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    elif device.type == "mps":
        torch.mps.synchronize()


def half_rotate(x):
    a, b = x.chunk(2, dim=-1)
    return torch.cat((-b, a), dim=-1)


def relocate(keys, source_positions, destination_positions, inv_freq):
    # Undo source RoPE, then apply destination RoPE under the SAME static schedule.
    #
    # Preserve the amplitude already in the keys. Two rotations avoid the long-position
    # fp32 phase-rounding error of computing only (destination - source) * inv_freq.
    def phase(positions):
        angles = torch.outer(torch.as_tensor(positions, device=keys.device).float(),
                             inv_freq.to(keys.device).float())
        angles = torch.cat((angles, angles), dim=-1)
        return angles.cos(), angles.sin()
    source_cos, source_sin = phase(source_positions)
    dest_cos, dest_sin = phase(destination_positions)
    x = keys.float()
    content = x * source_cos - half_rotate(x) * source_sin
    return (content * dest_cos + half_rotate(content) * dest_sin).to(keys.dtype)


def validate_pairs(sender, receiver, pairs):
    pairs = np.asarray(pairs)
    if pairs.ndim != 2 or pairs.shape[1] != 2 or pairs.dtype.kind not in "iu":
        raise ValueError("pairs must be an integer [n, 2] array")
    if len(pairs) and (np.any(pairs < 0) or np.any(pairs[:, 0] >= len(sender))
                       or np.any(pairs[:, 1] >= len(receiver))):
        raise ValueError("matched position outside prompt")
    if len(pairs) and (len(np.unique(pairs[:, 0])) != len(pairs)
                       or np.any(np.diff(pairs[:, 1]) <= 0)):
        raise ValueError("matched positions must be unique and receiver-ordered")
    if not np.array_equal(np.asarray(sender)[pairs[:, 0]], np.asarray(receiver)[pairs[:, 1]]):
        raise ValueError("archived matched tokens differ")


def blocks(pairs, recompute=()):
    # Return contiguous candidate-row runs; one-token matches are retained.
    rows = np.flatnonzero(~np.isin(np.arange(len(pairs)), recompute))
    if not len(rows):
        return []
    cuts = np.flatnonzero((np.diff(rows) != 1)
                         | (np.diff(pairs[rows, 0]) != 1)
                         | (np.diff(pairs[rows, 1]) != 1)) + 1
    return np.split(rows, cuts)


@torch.inference_mode()
def prefill(model, tokens, chunk, cache=None):
    cache = DynamicCache(config=model.config) if cache is None else cache
    tokens = torch.as_tensor(tokens, dtype=torch.long, device=model.device).reshape(1, -1)
    for start in range(0, tokens.shape[1], chunk):
        out = model(tokens[:, start:start + chunk], past_key_values=cache,
                    use_cache=True, logits_to_keep=1)
        cache = out.past_key_values
    return cache


def matched(cache, positions):
    # Retain only selected states on CPU, allowing the long sender cache to be freed.
    return [(layer.keys.index_select(-2, torch.as_tensor(positions, device=layer.keys.device)).cpu(),
             layer.values.index_select(-2, torch.as_tensor(positions, device=layer.values.device)).cpu())
            for layer in cache.layers]


def relocated_candidate(source, pairs, inv_freq, permutation=None):
    rows = np.arange(len(pairs)) if permutation is None else np.asarray(permutation)
    return [(relocate(k[:, :, rows], pairs[rows, 0], pairs[:, 1], inv_freq), v[:, :, rows])
            for k, v in source]


def random_candidate(fresh, reused, rng):
    # Isotropic null with exactly matched K/V error norms per token/layer/KV head.
    result = []
    for layer_fresh, layer_reused in zip(fresh, reused, strict=True):
        output = []
        for reference, candidate in zip(layer_fresh, layer_reused, strict=True):
            noise = torch.from_numpy(rng.standard_normal(reference.shape).astype(np.float32))
            norm = torch.linalg.vector_norm((candidate - reference).float(), dim=-1, keepdim=True)
            noise = noise / torch.linalg.vector_norm(noise, dim=-1, keepdim=True)
            output.append(reference + (noise * norm).to(reference.dtype))
        result.append(tuple(output))
    return result


def deviation_means(fresh, reused, pairs, inv_freq):
    # Current-runtime centered deviation, for a bridge to archived E9 moments.
    output = {}
    for kind, index in (("K", 0), ("V", 1)):
        means = []
        for reference, candidate in zip(fresh, reused, strict=True):
            ref, old = reference[index], candidate[index]
            if kind == "K":
                zero = np.zeros(len(pairs), dtype=np.int64)
                ref = relocate(ref, pairs[:, 1], zero, inv_freq)
                old = relocate(old, pairs[:, 1], zero, inv_freq)
            ref, old = ref.double(), old.double()
            denominator = ((ref - ref.mean(-2, keepdim=True)) ** 2).sum((-2, -1))
            if torch.any(denominator <= 0):
                raise ValueError("degenerate matched reference variance")
            means.append((((old - ref) ** 2).sum((-2, -1)) / denominator).mean().item())
        output[kind] = float(np.mean(means))
    return output


@torch.inference_mode()
def construct(model, receiver, pairs, candidate, chunk, recompute=()):
    # Copy selected states, then compute each gap against the assembled causal cache.
    #
    # A recomputed token reads reused predecessors. Selection may be oracle-informed;
    # this construction does not turn that selection into a deployable algorithm.
    sync(model.device)
    start = time.perf_counter()
    cache = DynamicCache(config=model.config)
    position = copied = 0
    for rows in blocks(pairs, recompute):
        destination = int(pairs[rows[0], 1])
        cache = prefill(model, receiver[position:destination], chunk, cache)
        if cache.get_seq_length() != destination:
            raise ValueError("cache length differs from destination position")
        for layer, (keys, values) in enumerate(candidate):
            cache.update(keys[:, :, rows].to(model.device), values[:, :, rows].to(model.device), layer)
        copied += len(rows)
        position = destination + len(rows)
    cache = prefill(model, receiver[position:], chunk, cache)
    sync(model.device)
    return cache, {"copied": copied, "recomputed": len(receiver) - copied,
                   "assembly_seconds": time.perf_counter() - start}


@torch.inference_mode()
def continuation_logits(model, cache, continuation, chunk):
    # Condition on C[0]; logits after C[:-1] predict C[1:]. C[0] is unscored.
    #
    # This keeps every matched receiver state eligible for reuse, including R[-1].
    # No extra prompt wrapper or silently recomputed final receiver token is used.
    if len(continuation) < 2:
        raise ValueError("at least two continuation tokens are needed")
    inputs = torch.as_tensor(continuation[:-1], dtype=torch.long, device=model.device)[None]
    logits = []
    for start in range(0, inputs.shape[1], chunk):
        out = model(inputs[:, start:start + chunk], past_key_values=cache, use_cache=True,
                    logits_to_keep=0)
        cache = out.past_key_values
        logits.append(out.logits[0].float().cpu())
    return torch.cat(logits)


def compare_logits(fresh, candidate):
    if (fresh.shape != candidate.shape or not torch.isfinite(fresh).all()
            or not torch.isfinite(candidate).all()):
        raise ValueError("invalid continuation logits")
    # Float64 on CPU makes a tiny negative KL from roundoff negligible.
    p = fresh.double().log_softmax(-1)
    q = candidate.double().log_softmax(-1)
    return {"kl": (p.exp() * (p - q)).sum(-1).clamp_min(0).numpy(),
            "top1_agrees": (fresh.argmax(-1) == candidate.argmax(-1)).numpy(),
            "max_logit_error": float((fresh - candidate).abs().max())}


def attention_reduce(query, keys, query_positions, delta, tail_mask, matched_mask, chunk=32):
    # Fresh causal attention-weighted error; Q heads map to their shared KV heads.
    #
    # query [Hq,Q,D], keys [Hkv,T,D], delta [T,Hkv]. Output [Q,Hq,3]:
    # weighted delta, mass on the paper's above-tolerance token set, and matched mass.
    groups = query.shape[0] // keys.shape[0]
    if groups * keys.shape[0] != query.shape[0]:
        raise ValueError("query/KV head counts do not divide")
    k = keys.repeat_interleave(groups, dim=0)
    d = delta.T.repeat_interleave(groups, dim=0)
    positions = torch.arange(k.shape[1], device=k.device)
    output = []
    for start in range(0, query.shape[1], chunk):
        q = query[:, start:start + chunk]
        scores = (q @ k.transpose(-1, -2)) / q.shape[-1] ** 0.5
        scores.masked_fill_(positions[None, None] > query_positions[start:start + chunk][None, :, None],
                            float("-inf"))
        weights = scores.float().softmax(-1)
        output.append(torch.stack(((weights * d[:, None]).sum(-1),
                                   (weights * tail_mask[None, None]).sum(-1),
                                   (weights * matched_mask[None, None]).sum(-1)), dim=-1).transpose(0, 1).cpu())
    return torch.cat(output)


class TailObserver:
    # Observe the last configured receiver queries without replacing SDPA's forward.
    def __init__(self, model, n_receiver, pairs, delta, n_queries, tau, chunk, tail_tokens=None):
        self.n_receiver, self.first = n_receiver, max(0, n_receiver - n_queries)
        self.delta, self.pairs, self.chunk = delta, pairs, chunk
        self.tail = delta.astype(np.float64).mean((1, 2)) > tau if tail_tokens is None else tail_tokens
        self.rows = {}
        self.handles = [layer.self_attn.register_forward_hook(self.observe, with_kwargs=True)
                        for layer in model.model.layers]

    @torch.inference_mode()
    def observe(self, module, args, kwargs, output):
        hidden = kwargs["hidden_states"] if "hidden_states" in kwargs else args[0]
        cache = kwargs["past_key_values"]
        keys = cache.layers[module.layer_idx].keys
        end = keys.shape[-2]
        start = end - hidden.shape[1]
        first = max(self.first, start)
        if first >= end or end > self.n_receiver:
            return
        q = module.q_norm(module.q_proj(hidden).view(1, hidden.shape[1], -1, module.head_dim))
        q = q.transpose(1, 2)
        cos, sin = kwargs["position_embeddings"]
        q = q * cos[:, None] + half_rotate(q) * sin[:, None]
        positions = torch.arange(first, end, device=q.device)
        delta = torch.zeros(end, keys.shape[1], device=q.device)
        mask = torch.zeros(end, device=q.device, dtype=torch.bool)
        matched_mask = torch.zeros_like(mask)
        included = self.pairs[:, 1] < end
        pr = torch.as_tensor(self.pairs[included, 1], device=q.device)
        delta[pr] = torch.as_tensor(self.delta[included, module.layer_idx], device=q.device,
                                   dtype=delta.dtype)
        mask[pr] = torch.as_tensor(self.tail[included], device=q.device)
        matched_mask[pr] = True
        reduced = attention_reduce(q[0, :, first - start:], keys[0], positions, delta, mask, matched_mask, self.chunk)
        self.rows.setdefault(module.layer_idx, []).append(reduced)

    def close(self):
        for handle in self.handles:
            handle.remove()
        return torch.stack([torch.cat(self.rows[layer]) for layer in sorted(self.rows)]).numpy()
