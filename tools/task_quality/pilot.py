# Task-quality pilot gate (ruling C2): item extraction over a cell, and the fresh-arm pilot on
# three handoffs. Fresh arm only: the receiver prefills its own prompt R and answers appended
# questions by greedy decoding. No cache is reused, nothing here is a registered cell.
import argparse
import hashlib
import json
import platform
import statistics
import subprocess
import time
import tomllib
from pathlib import Path

import numpy as np

from linear_ceiling.rng import make_rng
from .items import (KINDS, alignment_file, canonical_contains, contains, exact_match, first_span_exact,
                    handoff_texts, included_alignments, items_for_handoff, token_f1)

ROOT = Path(__file__).resolve().parents[2]
FORM2_KINDS = ("file", "signature")


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path, body):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(body, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_tokenizer(cfg):
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(cfg["model"], revision=cfg["revision"], local_files_only=True)
    if not tokenizer.is_fast:
        raise ValueError("a fast tokenizer is needed for character offsets")
    return tokenizer


def receiver_offsets(tokenizer, handoff, archived_receiver):
    encoded = tokenizer(handoff.receiver_text, add_special_tokens=False, return_offsets_mapping=True)
    if not np.array_equal(np.asarray(encoded["input_ids"]), archived_receiver):
        raise ValueError(f"tokenizer does not reproduce the archived receiver prompt: {handoff.handoff_id}")
    return encoded["offset_mapping"]


def extract_cell(args, cfg):
    """Items for every included handoff of one alignment pass; counts per handoff."""
    tokenizer = load_tokenizer(cfg)
    align_dir = ROOT / args.cell
    rows = included_alignments(align_dir)
    body = {"cell": args.cell, "coverage_sha256": digest(align_dir / "coverage.json"),
            "config_sha256": digest(args.config), "handoffs": []}
    for row in rows:
        hid = row["handoff_id"]
        trace_path, handoff = handoff_texts(args.traces, hid)
        text_sha = hashlib.sha256((handoff.sender_text + "\0" + handoff.receiver_text).encode()).hexdigest()
        if text_sha != row["text_sha256"]:
            raise ValueError(f"trace S/R differs from the archived handoff: {hid}")
        with np.load(alignment_file(align_dir, hid), allow_pickle=False) as arrays:
            receiver, pairs = arrays["receiver"], arrays["pairs"]
        offsets = receiver_offsets(tokenizer, handoff, receiver)
        items, counts = items_for_handoff(handoff.sender_text, handoff.receiver_text, offsets, pairs[:, 1])
        body["handoffs"].append({"handoff": hid, "n_sender": int(row["n_sender"]), "n_receiver": len(receiver),
                                 "n_matched": len(pairs), "trace_sha256": digest(trace_path),
                                 "alignment_sha256": digest(alignment_file(align_dir, hid)),
                                 "counts": counts, "items": items})
    write(args.output, body)
    return body


def counts_table(body):
    lines = []
    valid = [h["counts"]["valid"] for h in body["handoffs"]]
    form2 = [sum(h["counts"]["valid_by_kind"].get(k, 0) for k in FORM2_KINDS) for h in body["handoffs"]]
    lines.append(f"{body['cell']}: {len(valid)} handoffs; candidate lines {sum(h['counts']['candidate_lines'] for h in body['handoffs'])};"
                 f" distinct items {sum(h['counts']['distinct'] for h in body['handoffs'])};"
                 f" ambiguous keys {sum(h['counts']['ambiguous_keys'] for h in body['handoffs'])};"
                 f" in R {sum(h['counts']['in_receiver'] for h in body['handoffs'])}; valid {sum(valid)}")
    lines.append(f"  valid form-2' items per handoff: median {statistics.median(form2)} min {min(form2)} max {max(form2)};"
                 f" handoffs under 10: {sum(v < 10 for v in form2)}")
    by_kind = {k: sum(h["counts"]["valid_by_kind"].get(k, 0) for h in body["handoffs"]) for k in KINDS}
    lines.append(f"  valid by kind: {by_kind}")
    return "\n".join(lines)


def form2_count(handoff_row):
    return sum(handoff_row["counts"]["valid_by_kind"].get(kind, 0) for kind in FORM2_KINDS)


def pilot_handoffs(items_body, floor):
    # 0046's bridge rule over the handoffs the void rule keeps: shortest, middle and longest
    # sender among those with at least `floor` valid form-2' items.
    kept = sorted((h for h in items_body["handoffs"] if form2_count(h) >= floor),
                  key=lambda h: (h["n_sender"], h["handoff"]))
    if len(kept) < 3:
        raise ValueError("fewer than three handoffs reach the item floor")
    return [kept[0], kept[len(kept) // 2], kept[-1]]


def drawn_items(handoff_row, cfg, index):
    valid = [it for it in handoff_row["items"] if it["valid"]]
    form2 = sorted((it for it in valid if it["kind"] in FORM2_KINDS), key=lambda it: it["first_token"])
    if len(form2) > cfg["max_items_per_handoff"]:
        rng = make_rng(cfg["seed"] + index)
        chosen = sorted(rng.choice(len(form2), size=cfg["max_items_per_handoff"], replace=False).tolist())
        form2 = [form2[i] for i in chosen]
    repository = [it for it in valid if it["kind"] == "repository"]
    return form2 + repository[:1]


def question_for(item, cfg):
    template = cfg["questions"][item["kind"]]
    return template.format(cls=item.get("class", ""), method=item.get("method", ""))


def load_model(cfg, device):
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM
    model_cfg = AutoConfig.from_pretrained(cfg["model"], revision=cfg["revision"], local_files_only=True)
    model_cfg.rope_parameters = {**model_cfg.rope_parameters, **cfg["rope"]}
    model_cfg.max_position_embeddings = cfg["context_cap"]
    if device.type == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
    model = AutoModelForCausalLM.from_pretrained(cfg["model"], revision=cfg["revision"], config=model_cfg,
                                               dtype=torch.float32, attn_implementation="sdpa",
                                               local_files_only=True).eval().to(device)
    if model.model.rotary_emb.rope_type != "yarn":
        raise ValueError("the pilot uses the registered static YaRN schedule")
    return model


def greedy_answer(model, tokenizer, cache, prefix_length, question_ids, max_new_tokens, stop_ids,
                  stop_at_newline=False):
    # The cache holds inference tensors (core.prefill); every forward over it must stay in inference mode.
    import torch
    with torch.inference_mode():
        return _greedy(model, tokenizer, cache, prefix_length, question_ids, max_new_tokens, stop_ids, stop_at_newline)


def _greedy(model, tokenizer, cache, prefix_length, question_ids, max_new_tokens, stop_ids, stop_at_newline):
    import torch
    inputs = torch.as_tensor(question_ids, dtype=torch.long, device=model.device)[None]
    out = model(inputs, past_key_values=cache, use_cache=True, logits_to_keep=1)
    generated = []
    next_id = int(out.logits[0, -1].argmax())
    while len(generated) < max_new_tokens and next_id not in stop_ids:
        generated.append(next_id)
        if stop_at_newline and "\n" in tokenizer.decode(generated):
            break
        out = model(torch.tensor([[next_id]], device=model.device), past_key_values=out.past_key_values,
                    use_cache=True, logits_to_keep=1)
        next_id = int(out.logits[0, -1].argmax())
    appended = cache.get_seq_length() - prefix_length
    if appended:
        cache.crop(-appended)   # a negative count removes that many trailing tokens
    if cache.get_seq_length() != prefix_length:
        raise ValueError("cache did not return to the receiver prefix")
    return generated


def run(args, cfg):
    import torch
    import transformers
    from tools.cache_behavior.core import prefill
    items_body = json.loads(Path(args.items_file).read_text(encoding="utf-8"))
    if items_body["config_sha256"] != digest(args.config):
        raise ValueError("items were extracted under a different configuration")
    device = torch.device(args.device)
    tokenizer = load_tokenizer(cfg)
    model = load_model(cfg, device)
    stop_ids = {tokenizer.eos_token_id, tokenizer.convert_tokens_to_ids("<|endoftext|>")}
    identity = {"config_sha256": digest(args.config), "items_sha256": digest(args.items_file),
                "code_sha256": {name: digest(Path(__file__).with_name(name)) for name in ("pilot.py", "items.py")},
                "model": cfg["model"], "model_revision": cfg["revision"], "transformers": transformers.__version__,
                "torch": torch.__version__, "device": str(device), "dtype": "float32",
                "machine": platform.machine(), "system": platform.system()}
    report_path = args.output / "report.json"
    if report_path.exists():
        raise ValueError("pilot output exists; choose another --output")
    report = {"identity": identity, "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "rope": model.config.rope_parameters, "prompts": cfg["prompts"], "questions": cfg["questions"],
              "handoffs": [], "complete": False}
    picks = pilot_handoffs(items_body, cfg["min_form2_items"])
    for index, row in enumerate(picks):
        hid = row["handoff"]
        trace_path, handoff = handoff_texts(args.traces, hid)
        with np.load(alignment_file(ROOT / items_body["cell"], hid), allow_pickle=False) as arrays:
            receiver = arrays["receiver"]
        if digest(trace_path) != row["trace_sha256"]:
            raise ValueError(f"trace changed since extraction: {hid}")
        receiver_offsets(tokenizer, handoff, receiver)
        started = time.perf_counter()
        cache = prefill(model, receiver, cfg["chunk_tokens"])
        prefill_seconds = time.perf_counter() - started
        records = []
        for item in drawn_items(row, cfg, index):
            record = {key: item[key] for key in ("kind", "key", "answer", "first_token", "answer_tokens")}
            record["question"] = question_for(item, cfg)
            record["forms"] = {}
            for form, wrapper in cfg["prompts"].items():
                question_ids = tokenizer.encode(wrapper["before"] + record["question"] + wrapper["after"],
                                                add_special_tokens=False)
                started = time.perf_counter()
                generated = greedy_answer(model, tokenizer, cache, len(receiver), question_ids,
                                          cfg["max_new_tokens"], stop_ids, cfg["stop_at_newline"])
                prediction = tokenizer.decode(generated)
                record["forms"][form] = {"prediction": prediction, "generated_tokens": len(generated),
                                         "exact_match": exact_match(prediction, item["answer"]),
                                         "contains": contains(prediction, item["answer"]),
                                         "token_f1": token_f1(prediction, item["answer"]),
                                         "seconds": time.perf_counter() - started}
            records.append(record)
            print(f"{hid} {item['kind']} {item['key']}: " + " | ".join(
                f"{form}={'EM' if r['exact_match'] else 'contains' if r['contains'] else f'F1 {r['token_f1']:.2f}'}"
                for form, r in record["forms"].items()),
                flush=True)
        del cache
        report["handoffs"].append({"handoff": hid, "n_sender": row["n_sender"], "n_receiver": len(receiver),
                                   "prefill_seconds": prefill_seconds, "items": records})
        report["complete"] = len(report["handoffs"]) == len(picks)
        write(report_path, report)
        print(json.dumps({f: {k: v for k, v in body.items() if k.startswith("median")}
                          for f, body in summarize(args.output)["forms"].items()}, indent=1), flush=True)


SCORERS = ("exact_match", "contains", "token_f1", "first_span_exact", "canonical_contains")


def scores_for(prediction, gold, kind):
    return {"exact_match": exact_match(prediction, gold), "contains": contains(prediction, gold),
            "token_f1": token_f1(prediction, gold), "first_span_exact": first_span_exact(prediction, gold, kind),
            "canonical_contains": canonical_contains(prediction, gold)}


def summarize(output):
    """Fail-closed reader: every score derived from the stored prediction and gold. The three
    scores the run stored must reproduce; the two added after the pilot's first reading
    (first def-span exact match, containment after canonicalization) are derived here only."""
    report = json.loads((Path(output) / "report.json").read_text(encoding="utf-8"))
    cfg = tomllib.loads((ROOT / "config/task-quality-pilot.toml").read_text(encoding="utf-8"))
    if report["identity"]["config_sha256"] != digest(ROOT / "config/task-quality-pilot.toml"):
        raise ValueError("report was produced under a different configuration")
    forms = list(report["prompts"])
    per_handoff = {form: [] for form in forms}
    by_kind = {form: {kind: [] for kind in KINDS} for form in forms}
    for handoff in report["handoffs"]:
        if not any(it["kind"] in FORM2_KINDS for it in handoff["items"]):
            raise ValueError(f"no form-2' items scored: {handoff['handoff']}")
        for form in forms:
            form2 = []
            for it in handoff["items"]:
                stored = it["forms"][form]
                scores = scores_for(stored["prediction"], it["answer"], it["kind"])
                if (stored["exact_match"] != scores["exact_match"] or stored["contains"] != scores["contains"]
                        or abs(stored["token_f1"] - scores["token_f1"]) > 1e-12):
                    raise ValueError("stored score differs from the recomputed one")
                by_kind[form][it["kind"]].append(scores)
                if it["kind"] in FORM2_KINDS:
                    form2.append(scores)
            per_handoff[form].append({"handoff": handoff["handoff"], "n_form2": len(form2),
                                      **{key: float(np.mean([r[key] for r in form2])) for key in SCORERS}})
    low, high = cfg["gate"]
    body = {"complete": report["complete"], "handoffs": len(report["handoffs"]),
            "interpretation": "Fresh-arm pilot on three handoffs; a power gate, not a registered result.",
            "gate": cfg["gate"], "forms": {}}
    for form in forms:
        medians = {key: statistics.median([h[key] for h in per_handoff[form]]) for key in SCORERS}
        body["forms"][form] = {
            "per_handoff": per_handoff[form],
            "median_exact_match": medians["exact_match"],
            "median_contains": medians["contains"],
            "median_token_f1": medians["token_f1"],
            "median_first_span_exact": medians["first_span_exact"],
            "median_canonical_contains": medians["canonical_contains"],
            "within_gate": {key: (bool(low <= medians[key] <= high) if report["complete"] else None)
                            for key in ("exact_match", "contains", "first_span_exact", "canonical_contains")},
            "by_kind": {kind: {"n": len(rows), **{key: float(np.mean([r[key] for r in rows])) for key in SCORERS}}
                        for kind, rows in by_kind[form].items() if rows}}
    write(Path(output) / "summary.json", body)
    return body


def main():
    parser = argparse.ArgumentParser(description="Task-quality pilot gate (fresh arm only)")
    action = parser.add_mutually_exclusive_group(required=True)
    for name in ("items", "run", "summarize"):
        action.add_argument(f"--{name}", action="store_true")
    parser.add_argument("--config", type=Path, default=ROOT / "config/task-quality-pilot.toml")
    parser.add_argument("--cell", default=None, help="alignment pass, e.g. results/e9l/align")
    parser.add_argument("--traces", type=Path, default=ROOT / "traces")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--items-file", type=Path, help="--run: the items file written by --items")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    cfg = tomllib.loads(args.config.read_text(encoding="utf-8"))
    if args.items:
        args.cell = args.cell or cfg["cell_align"]
        print(counts_table(extract_cell(args, cfg)))
    elif args.run:
        if args.items_file is None:
            parser.error("--run requires --items-file (the --items output for the long cell)")
        run(args, cfg)
    else:
        print(json.dumps(summarize(args.output), indent=2))


if __name__ == "__main__":
    main()
