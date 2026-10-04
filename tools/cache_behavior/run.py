# Prepare, check, run/resume, and summarize descriptive long-Qwen cache readout.
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tomllib

import numpy as np
import torch
import transformers
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

from linear_ceiling.e7_stats import quantile, summary
from linear_ceiling.e7_swe import _flatten_nodes, _llmresult_texts, load_composio_detailed
from linear_ceiling.e9_align import handoffs_from
from linear_ceiling.e9_pertoken import centered_delta, token_mean
from linear_ceiling.rng import make_rng
from .core import (TailObserver, compare_logits, construct, continuation_logits, deviation_means,
                   matched, prefill, random_candidate, relocated_candidate, sync, validate_pairs)

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path, body):
    path = Path(path)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(body, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def continuation_from(path, handoff_id):
    # Use the same parsed assistant-turn index as E9; never guess a nearby response.
    trajectory, texts = load_composio_detailed(path, path.parent.name, lambda text, kind: 0)
    handoff = next(h for h in handoffs_from(trajectory, texts) if h.handoff_id == handoff_id)
    assistants = [i for i, msg in enumerate(trajectory.messages) if msg.role == "assistant"]
    index = assistants[handoff.switch_index]
    request = trajectory.messages[index].request
    responses = [text for node in _flatten_nodes(json.loads(path.read_text())[request])
                 for text in _llmresult_texts(node)]
    if texts[index] not in responses:
        raise ValueError("selected assistant turn is prompt history, not the recorded response")
    return handoff, texts[index]


def prepare(args, cfg):
    report_path = args.archive / "report.json"
    evidence = {str((args.evidence_sha256.parent / line.split(None, 1)[1]).resolve()): line.split(None, 1)[0]
                for line in args.evidence_sha256.read_text().splitlines() if line.strip()}
    def verified_digest(path):
        actual = digest(path)
        if evidence.get(str(path.resolve())) != actual:
            raise ValueError(f"archive file differs from evidence SHA256SUMS: {path}")
        return actual
    report_sha = verified_digest(report_path)
    archived = json.loads(report_path.read_text())
    e9_config = ROOT / "config/e9l.toml"
    corpus_path = ROOT / "config/e7-manifest.json"
    corpus = {row["path"]: row for row in json.loads(corpus_path.read_text())["files"]}
    if (not archived["complete"] or len(archived["run_order"]) != cfg["expected_handoffs"]
            or archived["config_sha256"] != digest(e9_config)):
        raise ValueError("expected complete original E9-long archive and unchanged config")
    tokenizer = AutoTokenizer.from_pretrained(cfg["model"], revision=cfg["revision"], local_files_only=True)
    args.inputs.mkdir(parents=True, exist_ok=True)
    if (args.inputs / "manifest.json").exists():
        raise ValueError("prepared manifest already exists; check it instead of overwriting")
    manifest = {"config_sha256": digest(args.config), "archive_report_sha256": report_sha,
                "archive_config_sha256": digest(e9_config), "corpus_manifest_sha256": digest(corpus_path),
                "evidence_sha256_manifest": digest(args.evidence_sha256), "records": []}
    alignments = {row["handoff_id"]: row for row in archived["alignments"]}
    for hid in archived["run_order"]:
        stem = hid.replace("/", "__").replace("#", "_sw")
        alignment = args.archive / "align" / f"{stem}.npz"
        score = archived["scores"][hid]
        score_path = args.archive / "scores" / score["score_file"]
        token_path = args.archive / "tokens" / score["tokens_file"]
        if verified_digest(score_path) != score["score_sha256"] or verified_digest(token_path) != score["tokens_sha256"]:
            raise ValueError(f"archive hash mismatch: {hid}")
        alignment_sha = verified_digest(alignment)
        trace_relative = "swe-bench/" + hid.split("#")[0] + ".json"
        trace_path = args.traces / trace_relative
        if digest(trace_path) != corpus[trace_relative]["sha256"]:
            raise ValueError(f"trace differs from original corpus manifest: {trace_relative}")
        handoff, text = continuation_from(trace_path, hid)
        text_sha = hashlib.sha256((handoff.sender_text + "\0" + handoff.receiver_text).encode()).hexdigest()
        if text_sha != alignments[hid]["text_sha256"]:
            raise ValueError(f"trace S/R differs from archived handoff: {hid}")
        with np.load(alignment, allow_pickle=False) as source:
            sender, receiver, pairs = (source[key] for key in ("sender", "receiver", "pairs"))
        validate_pairs(sender, receiver, pairs)
        for actual, expected in ((sender, handoff.sender_text), (receiver, handoff.receiver_text)):
            if not np.array_equal(actual, tokenizer.encode(expected, add_special_tokens=False)):
                raise ValueError(f"tokenizer does not reproduce archived prompt: {hid}")
        continuation = np.asarray(tokenizer.encode(text, add_special_tokens=False)[:cfg["continuation_tokens"]],
                                  dtype=np.int64)
        body = json.loads(score_path.read_text())
        with np.load(token_path, allow_pickle=False) as tokens:
            delta = centered_delta(tokens["same_K"], np.array([row["sst"] for row in body["same"]["K"]]), len(pairs))
        path = args.inputs / f"{stem}.npz"
        np.savez_compressed(path, sender=sender, receiver=receiver, pairs=pairs, continuation=continuation,
                            delta_K=delta.astype(np.float32), tail_K=token_mean(delta) > cfg["tau_K"])
        manifest["records"].append({"handoff": hid, "file": path.name, "sha256": digest(path),
                                    "sender_tokens": len(sender), "receiver_tokens": len(receiver),
                                    "continuation_tokens": len(continuation),
                                    "excluded": len(continuation) < 2,
                                    "reason": "fewer than two recorded continuation tokens" if len(continuation) < 2 else None,
                                    "archive_alignment_sha256": alignment_sha,
                                    "archive_score_sha256": digest(score_path),
                                    "archive_tokens_sha256": digest(token_path), "trace_sha256": digest(trace_path),
                                    "continuation_text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                                    "archived_mean": {key: 1 - score[f"same_{key}_r2_layer_mean"] for key in ("K", "V")}})
    write(args.inputs / "manifest.json", manifest)
    print(f"Prepared {len(manifest['records'])} handoffs; run --check before GPU use.")


def check(args, cfg):
    if transformers.__version__ != cfg["transformers"] or torch.__version__.split("+")[0] != cfg["torch"]:
        raise ValueError("runtime differs from pinned experiment versions")
    manifest = json.loads((args.inputs / "manifest.json").read_text())
    if (manifest["config_sha256"] != digest(args.config)
            or manifest["corpus_manifest_sha256"] != digest(ROOT / "config/e7-manifest.json")
            or manifest["archive_config_sha256"] != digest(ROOT / "config/e9l.toml")):
        raise ValueError("configuration changed after preparation")
    if len(manifest["records"]) != cfg["expected_handoffs"]:
        raise ValueError("input cohort is incomplete")
    ordered_records(manifest)
    for row in manifest["records"]:
        if digest(args.inputs / row["file"]) != row["sha256"]:
            raise ValueError(f"input hash mismatch: {row['file']}")
        with np.load(args.inputs / row["file"], allow_pickle=False) as arrays:
            validate_pairs(arrays["sender"], arrays["receiver"], arrays["pairs"])
            if len(arrays["delta_K"]) != len(arrays["pairs"]):
                raise ValueError("archived deviation/matched-set mismatch")
    return manifest


def metrics(arrays):
    return {"mean_kl": float(np.mean(arrays["kl"])), "p90_kl": quantile(arrays["kl"].tolist(), 0.9),
            "top1_agreement": float(np.mean(arrays["top1_agrees"]))}


def ordered_records(manifest):
    included = [row for row in manifest["records"] if not row["excluded"]]
    if not included or len({row["handoff"] for row in manifest["records"]}) != len(manifest["records"]):
        raise ValueError("prepared cohort must have unique handoffs and a nonempty included set")
    largest = max(included, key=lambda row: row["sender_tokens"])
    return [largest] + [row for row in included if row != largest]


def summarize(output, inputs=None):
    report = json.loads((output / "report.json").read_text())
    order, scored = report["run_order"], list(report["scores"])
    if not order or len(set(order)) != len(order) or scored != order[:len(scored)]:
        raise ValueError("scored handoffs must be a prefix of the unique run_order")
    if report["complete"] is not (len(scored) == len(order)):
        raise ValueError("complete flag does not match scored cohort coverage")
    if inputs is not None:
        manifest_path = inputs / "manifest.json"
        if report["identity"]["manifest_sha256"] != digest(manifest_path):
            raise ValueError("report refers to a different prepared manifest")
        manifest = json.loads(manifest_path.read_text())
        if (order != [row["handoff"] for row in ordered_records(manifest)]
                or report["excluded"] != [row for row in manifest["records"] if row["excluded"]]):
            raise ValueError("report cohort differs from the prepared manifest")
    rows, attention_rows = [], []
    for index, result in enumerate(report["scores"].values()):
        if digest(output / result["file"]) != result["sha256"]:
            raise ValueError("output hash mismatch")
        with np.load(output / result["file"], allow_pickle=False) as arrays:
            n = result["scored_continuation_tokens"]
            if n < 1 or len(arrays["continuation"]) != n + 1:
                raise ValueError("stored continuation differs from scored token count")
            for arm in result["arms"]:
                kl, top1 = arrays[f"{arm}_kl"], arrays[f"{arm}_top1_agrees"]
                if (kl.shape != (n,) or top1.shape != (n,) or top1.dtype != np.bool_
                        or not np.isfinite(kl).all() or np.any(kl < 0)):
                    raise ValueError(f"incomplete or invalid per-token metrics: {arm}")
            witness_count = result["witness_count"]
            if witness_count != (min(4, n) if index == 0 else 0):
                raise ValueError("missing or incomplete first-handoff logits witness")
            if witness_count:
                if (arrays["fresh_witness"].shape[0] != witness_count
                        or not np.array_equal(arrays["witness_continuation_indices"],
                                              np.arange(1, witness_count + 1))):
                    raise ValueError("logits witness covers the wrong continuation positions")
                for arm in result["arms"]:
                    witness = compare_logits(torch.from_numpy(arrays["fresh_witness"]),
                                             torch.from_numpy(arrays[f"{arm}_witness"]))
                    if (not np.allclose(witness["kl"], arrays[f"{arm}_kl"][:witness_count], atol=1e-10, rtol=1e-10)
                            or not np.array_equal(witness["top1_agrees"], arrays[f"{arm}_top1_agrees"][:witness_count])):
                        raise ValueError(f"saved logits witness does not reproduce {arm}'s scored positions")
            rows.append({arm: metrics({key: arrays[f"{arm}_{key}"] for key in ("kl", "top1_agrees")})
                         for arm in result["arms"]})
            attention = arrays["attention"]
            row = {f"{name}_{stat}": reducer(attention[..., index].flatten())
                   for index, name in enumerate(("weighted_delta", "tail_attention_mass", "matched_attention_mass"))
                   for stat, reducer in (("mean", lambda x: float(np.mean(x))),
                                         ("p90", lambda x: quantile(x.tolist(), .9)))}
            defined = attention[..., 2] > 0
            conditional = attention[..., 0][defined] / attention[..., 2][defined]
            row["conditional_weighted_delta_mean"] = float(conditional.mean()) if len(conditional) else None
            row["conditional_weighted_delta_p90"] = quantile(conditional.tolist(), .9) if len(conditional) else None
            row["conditional_undefined_count"] = int((~defined).sum())
            attention_rows.append(row)
    body = {"complete": report["complete"], "scored": len(rows), "excluded": report["excluded"],
            "interpretation": "Prediction sensitivity on a fixed continuation; no task-quality verdict.",
            "arms": {arm: {key: summary([row[arm][key] for row in rows])
                           for key in ("mean_kl", "p90_kl", "top1_agreement")}
                     for arm in rows[0]} if rows else {},
            "attention": {key: summary([row[key] for row in attention_rows if row[key] is not None])
                          if any(row[key] is not None for row in attention_rows) else None
                          for key in attention_rows[0]} if attention_rows else {}}
    write(output / "summary.json", body)
    return body


def run(args, cfg, manifest):
    # Keep the numeric budgets; display labels must never round the selected fraction.
    arm_fractions = [("reuse", 0), ("random", 0), ("scrambled", 0)] + [
        (f"oracle_ranked_{f * 100:g}pct", f) for f in cfg["oracle_fractions"]]
    if (any(not 0 < f <= 1 for f in cfg["oracle_fractions"])
            or len({arm for arm, _ in arm_fractions}) != len(arm_fractions)):
        raise ValueError("oracle fractions must be in (0, 1] with distinct labels")
    # Set before loading CUDA tensors; deterministic cuBLAS otherwise refuses GEMMs.
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    if os.environ["CUBLAS_WORKSPACE_CONFIG"] != ":4096:8":
        raise ValueError("this run pins CUBLAS_WORKSPACE_CONFIG=:4096:8")
    device = torch.device(args.device)
    if device.type != "cuda":
        raise ValueError("long-cohort runs require CUDA; CPU correctness tests are separate")
    model_cfg = AutoConfig.from_pretrained(cfg["model"], revision=cfg["revision"], local_files_only=True)
    model_cfg.rope_parameters = {**model_cfg.rope_parameters, **cfg["rope"]}
    model_cfg.max_position_embeddings = cfg["context_cap"]
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.use_deterministic_algorithms(True)
    model = AutoModelForCausalLM.from_pretrained(cfg["model"], revision=cfg["revision"], config=model_cfg,
                                               dtype=torch.float32, attn_implementation="sdpa",
                                               local_files_only=True).eval().to(device)
    if model.model.rotary_emb.rope_type != "yarn":
        raise ValueError("this run supports the registered static YaRN schedule only")
    freq = model.model.rotary_emb.inv_freq.detach().cpu()
    args.output.mkdir(parents=True, exist_ok=True)
    report_path = args.output / "report.json"
    source_hashes = {name: digest(Path(__file__).with_name(name)) for name in ("run.py", "core.py")}
    identity = {"config_sha256": digest(args.config), "manifest_sha256": digest(args.inputs / "manifest.json"),
                "code_sha256": source_hashes, "transformers": transformers.__version__, "torch": torch.__version__,
                "gpu": torch.cuda.get_device_name(device), "cuda": torch.version.cuda,
                "cublas_workspace_config": os.environ["CUBLAS_WORKSPACE_CONFIG"]}
    if report_path.exists():
        if not args.resume:
            raise ValueError("output exists; pass --resume to verify and continue")
        report = json.loads(report_path.read_text())
        if report["identity"] != identity:
            raise ValueError("resume identity differs (code, inputs, configuration, runtime, or GPU)")
        summarize(args.output, args.inputs)
    else:
        report = {"identity": identity, "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  "model": cfg["model"], "model_revision": cfg["revision"],
                  "rope": model_cfg.rope_parameters, "attention_scaling": model.model.rotary_emb.attention_scaling,
                  "inv_freq_sha256": hashlib.sha256(freq.numpy().tobytes()).hexdigest(),
                  "scores": {}, "excluded": [r for r in manifest["records"] if r["excluded"]], "complete": False}
    order = ordered_records(manifest)
    report["run_order"] = [r["handoff"] for r in order]
    write(report_path, report)
    for index, record in enumerate(order[:1] if args.probe else order):
        hid = record["handoff"]
        if hid in report["scores"]:
            continue
        with np.load(args.inputs / record["file"], allow_pickle=False) as arrays:
            sender, receiver, pairs, continuation, delta, tail = (arrays[key] for key in
                                                                ("sender", "receiver", "pairs", "continuation", "delta_K", "tail_K"))
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(device)
        observer = TailObserver(model, len(receiver), pairs, delta, cfg["attention_queries"],
                                cfg["tau_K"], cfg["attention_query_chunk"], tail)
        cache = prefill(model, receiver, cfg["chunk_tokens"])
        attention = observer.close()
        fresh_states = matched(cache, pairs[:, 1])
        fresh_logits = continuation_logits(model, cache, continuation, cfg["continuation_chunk"])
        del cache
        # Identical repeat and a real prefix-copy control once, on the largest handoff.
        controls = {}
        if index == 0:
            repeat = prefill(model, receiver, cfg["chunk_tokens"])
            compared = compare_logits(fresh_logits, continuation_logits(
                model, repeat, continuation, cfg["continuation_chunk"]))
            controls["fresh_repeat"] = {**metrics(compared), "max_logit_error": compared["max_logit_error"]}
            del repeat
            prefix_n = min(cfg["prefix_control_tokens"], len(receiver))
            prefix = prefill(model, receiver[:prefix_n], cfg["chunk_tokens"])
            prefix_pairs = np.column_stack((np.arange(prefix_n), np.arange(prefix_n)))
            prefix_states = matched(prefix, np.arange(prefix_n))
            del prefix
            copied, _ = construct(model, receiver, prefix_pairs, prefix_states, cfg["chunk_tokens"])
            compared = compare_logits(fresh_logits, continuation_logits(
                model, copied, continuation, cfg["continuation_chunk"]))
            controls["prefix_copy"] = {**metrics(compared), "max_logit_error": compared["max_logit_error"]}
            del copied, prefix_states
            if max(c["max_logit_error"] for c in controls.values()) > cfg["control_max_logit_error"]:
                raise ValueError(f"fresh/prefix identity control failed: {controls}")
        sender_cache = prefill(model, sender, cfg["chunk_tokens"])
        source = matched(sender_cache, pairs[:, 0])
        del sender_cache
        reused = relocated_candidate(source, pairs, freq)
        bridge = deviation_means(fresh_states, reused, pairs, freq)
        for key in ("K", "V"):
            reference = record["archived_mean"][key]
            if abs(bridge[key] - reference) > cfg["bridge_absolute_tolerance"] + cfg["bridge_relative_tolerance"] * abs(reference):
                raise ValueError(f"archive/runtime deviation bridge failed: {hid} {key} {bridge[key]} vs {reference}")
        outputs = {"attention": attention, "continuation": continuation,
                   "receiver_query_positions":
                   np.arange(max(0, len(receiver) - cfg["attention_queries"]), len(receiver))}
        witness_count = min(4, len(fresh_logits)) if index == 0 else 0
        if witness_count:
            outputs.update(fresh_witness=fresh_logits[:witness_count].numpy(),
                           witness_continuation_indices=np.arange(1, witness_count + 1))
        arms = {}
        for arm, fraction in arm_fractions:
            candidate, removed = reused, []
            if arm == "random":
                candidate = random_candidate(fresh_states, reused, make_rng(cfg["seed"] + index))
            elif arm == "scrambled":
                candidate = relocated_candidate(source, pairs, freq, np.roll(np.arange(len(pairs)), len(pairs) // 2))
            elif arm.startswith("oracle_ranked_"):
                removed = np.argsort(-token_mean(delta), kind="stable")[:int(np.ceil(len(pairs) * fraction))]
            cache, counts = construct(model, receiver, pairs, candidate, cfg["chunk_tokens"], removed)
            logits = continuation_logits(model, cache, continuation, cfg["continuation_chunk"])
            compared = compare_logits(fresh_logits, logits)
            outputs.update({f"{arm}_{key}": compared[key] for key in ("kl", "top1_agrees")})
            if witness_count:
                outputs[f"{arm}_witness"] = logits[:witness_count].numpy()
            arms[arm] = {**counts, **metrics(compared)}
            del cache, logits, candidate
            gc.collect()
        sync(device)
        destination = args.output / record["file"]
        np.savez_compressed(destination, **outputs)
        report["scores"][hid] = {"file": destination.name, "sha256": digest(destination), "arms": arms,
                                  "controls": controls, "archive_bridge_mean": bridge,
                                  "witness_count": witness_count,
                                  "scored_continuation_tokens": len(continuation) - 1,
                                  "peak_allocated_GiB": torch.cuda.max_memory_allocated(device) / 2**30}
        report["complete"] = len(report["scores"]) == len(order)
        write(report_path, report)
        summarize(args.output, args.inputs)
        print(f"{len(report['scores'])}/{len(order)} {hid}", flush=True)
        del source, reused, fresh_states, fresh_logits


def main():
    parser = argparse.ArgumentParser(description="Long-Qwen cache readout")
    action = parser.add_mutually_exclusive_group(required=True)
    for name in ("prepare", "check", "run", "probe", "summarize"):
        action.add_argument(f"--{name}", action="store_true")
    parser.add_argument("--config", type=Path, default=ROOT / "config/cache-behavior.toml")
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--traces", type=Path)
    parser.add_argument("--evidence-sha256", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    cfg = tomllib.loads(args.config.read_text())
    if args.prepare:
        if args.archive is None or args.traces is None or args.evidence_sha256 is None:
            parser.error("--prepare requires --archive, --traces, and --evidence-sha256")
        prepare(args, cfg)
    elif args.summarize:
        if args.output is None:
            parser.error("--summarize requires --output")
        check(args, cfg)
        print(json.dumps(summarize(args.output, args.inputs), indent=2))
    else:
        manifest = check(args, cfg)
        if args.check:
            print(f"Inputs and runtime verified: {len(manifest['records'])} handoffs; GPU controls pending.")
        else:
            if args.output is None:
                parser.error("--run/--probe requires --output")
            run(args, cfg, manifest)


if __name__ == "__main__":
    main()
