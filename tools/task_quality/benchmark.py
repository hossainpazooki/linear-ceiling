# Benchmark control pilot (plan 2026-10-13 §5, ground-truth source B): a public QA set composed into
# a standalone handoff, fresh arm only, so a retention statistic in the cell can later be read beside
# a number other groups report. Composition is one rendering among possible ones; the config states it.
# Nothing here is a registered cell.
import argparse
import json
import platform
import statistics
import subprocess
import time
import tomllib
from pathlib import Path

import numpy as np

from .longbench_metrics import best_over_answers
from .pilot import ROOT, digest, greedy_answer, load_model, load_tokenizer, same_text, text_digest, write

CODE = ("benchmark.py", "longbench_metrics.py", "pilot.py")


def load_set(cfg, name):
    spec = cfg["data"]["sets"][name]
    path = ROOT / spec["path"]
    if digest(path) != spec["sha256"]:
        raise ValueError(f"data file differs from its pinned sha: {name}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def tool_result(cfg, context):
    # The traces render a tool result as JSON on one line; the passage takes the same form in S and R.
    return json.dumps({"data": {cfg["composition"]["tool_key"]: context}}, ensure_ascii=False)


def compose(cfg, context):
    """S and R for one passage, with the rendered passage's character span in each."""
    c = cfg["composition"]
    rendered = tool_result(cfg, context)
    sender_head = c["sender_system"] + c["sender_before"]
    return {"sender": sender_head + rendered + c["sender_after"],
            "receiver": c["receiver_prefix"] + rendered + c["receiver_suffix"],
            "sender_span": [len(sender_head), len(sender_head) + len(rendered)],
            "receiver_span": [len(c["receiver_prefix"]), len(c["receiver_prefix"]) + len(rendered)]}


def encode(tokenizer, text):
    encoded = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
    return list(encoded["input_ids"]), encoded["offset_mapping"]


def token_span(offsets, start, end):
    # [first, last + 1) over the tokens that overlap the character span.
    starts = np.asarray([s for s, _ in offsets], dtype=np.int64)
    ends = np.asarray([e for _, e in offsets], dtype=np.int64)
    tokens = np.flatnonzero((starts < end) & (ends > start))
    if not len(tokens):
        raise ValueError("character span covers no token")
    return [int(tokens[0]), int(tokens[-1]) + 1]


def item_table(cfg, tokenizer, rows):
    """Per item: lengths of S and R and the passage's token span in each (the seam positions)."""
    table = []
    for index, row in enumerate(rows):
        comp = compose(cfg, row["context"])
        sender_ids, sender_offsets = encode(tokenizer, comp["sender"])
        receiver_ids, receiver_offsets = encode(tokenizer, comp["receiver"])
        table.append({"index": index, "id": row["_id"], "n_sender": len(sender_ids), "n_receiver": len(receiver_ids),
                      "sender_passage_tokens": token_span(sender_offsets, *comp["sender_span"]),
                      "receiver_passage_tokens": token_span(receiver_offsets, *comp["receiver_span"]),
                      "n_answers": len(row["answers"])})
    return table


def pilot_items(table):
    # Shortest, middle and longest receiver prompt (the same bridge rule as the task-quality pilot).
    ordered = sorted(table, key=lambda t: (t["n_receiver"], t["index"]))
    if len(ordered) < 3:
        raise ValueError("fewer than three items in the set")
    return [ordered[0], ordered[len(ordered) // 2], ordered[-1]]


def identity_of(cfg, args, device):
    import torch
    import transformers
    return {"config_sha256": text_digest(args.config),
            "data_sha256": {name: spec["sha256"] for name, spec in cfg["data"]["sets"].items()},
            "code_sha256": {name: text_digest(Path(__file__).with_name(name)) for name in CODE},
            "model": cfg["model"], "model_revision": cfg["revision"], "transformers": transformers.__version__,
            "torch": torch.__version__, "device": str(device), "dtype": "float32",
            "machine": platform.machine(), "system": platform.system()}


def table_only(args, cfg):
    tokenizer = load_tokenizer(cfg)
    body = {"config_sha256": text_digest(args.config), "sets": {}}
    for name in cfg["data"]["sets"]:
        table = item_table(cfg, tokenizer, load_set(cfg, name))
        lengths = sorted(t["n_receiver"] for t in table)
        body["sets"][name] = {"n_items": len(table), "receiver_tokens": {"min": lengths[0], "median": lengths[len(lengths) // 2],
                                                                        "max": lengths[-1], "sum": sum(lengths)},
                              "pilot": [t["id"] for t in pilot_items(table)], "items": table}
        print(f"{name}: {len(table)} items; receiver tokens min {lengths[0]} median {lengths[len(lengths) // 2]}"
              f" max {lengths[-1]}; pilot {[t['index'] for t in pilot_items(table)]}", flush=True)
    write(args.output / "table.json", body)
    return body


def run(args, cfg):
    import torch
    from tools.cache_behavior.core import prefill
    device = torch.device(args.device)
    tokenizer = load_tokenizer(cfg)
    model = load_model(cfg, device)
    stop_ids = {tokenizer.eos_token_id, tokenizer.convert_tokens_to_ids("<|endoftext|>")}
    report_path = args.output / "report.json"
    if report_path.exists():
        raise ValueError("pilot output exists; choose another --output")
    report = {"identity": identity_of(cfg, args, device),
              "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "rope": model.config.rope_parameters, "composition": cfg["composition"], "question": cfg["question"],
              "prompts": cfg["prompts"], "sets": {}, "complete": False}
    names = list(cfg["data"]["sets"])
    for name in names:
        rows = load_set(cfg, name)
        table = item_table(cfg, tokenizer, rows)
        records = []
        for entry in pilot_items(table):
            row = rows[entry["index"]]
            receiver_ids, _ = encode(tokenizer, compose(cfg, row["context"])["receiver"])
            question = cfg["question"].format(input=row["input"])
            started = time.perf_counter()
            cache = prefill(model, np.asarray(receiver_ids), cfg["chunk_tokens"])
            record = {**entry, "question": question, "answers": row["answers"],
                      "prefill_seconds": time.perf_counter() - started, "forms": {}}
            for form, wrapper in cfg["prompts"].items():
                question_ids = tokenizer.encode(wrapper["before"] + question + wrapper["after"], add_special_tokens=False)
                started = time.perf_counter()
                generated = greedy_answer(model, tokenizer, cache, len(receiver_ids), question_ids,
                                          cfg["max_new_tokens"], stop_ids, cfg["stop_at_newline"])
                prediction = tokenizer.decode(generated)
                record["forms"][form] = {"prediction": prediction, "generated_tokens": len(generated),
                                         "qa_f1": best_over_answers(prediction, row["answers"]),
                                         "seconds": time.perf_counter() - started}
                # No-context control: the same question under the same form with no passage before it.
                control_ids = tokenizer.encode(wrapper["before"].lstrip("\n") + question + wrapper["after"],
                                               add_special_tokens=False)
                control = prefill(model, np.asarray(control_ids[:-1]), cfg["chunk_tokens"])
                generated = greedy_answer(model, tokenizer, control, len(control_ids) - 1, control_ids[-1:],
                                          cfg["max_new_tokens"], stop_ids, cfg["stop_at_newline"])
                del control
                prediction = tokenizer.decode(generated)
                record["forms"][form]["no_context"] = {"prediction": prediction, "generated_tokens": len(generated),
                                                       "qa_f1": best_over_answers(prediction, row["answers"])}
            del cache
            records.append(record)
            print(f"{name} #{entry['index']} (R {entry['n_receiver']}): " + " | ".join(
                f"{form}={r['qa_f1']:.2f} (no context {r['no_context']['qa_f1']:.2f})" for form, r in record["forms"].items()),
                flush=True)
        report["sets"][name] = {"n_items": len(rows), "table": table, "items": records}
        report["complete"] = len(report["sets"]) == len(names)
        write(report_path, report)
        print(json.dumps({f: {s: b["median_qa_f1"] for s, b in sets.items()}
                          for f, sets in summarize(args.output)["forms"].items()}), flush=True)


def summarize(output):
    """Fail-closed reader: every F1 recomputed from the stored prediction and answers."""
    report = json.loads((Path(output) / "report.json").read_text(encoding="utf-8"))
    cfg = tomllib.loads((ROOT / "config/benchmark-control-pilot.toml").read_text(encoding="utf-8"))
    if not same_text(report["identity"]["config_sha256"], ROOT / "config/benchmark-control-pilot.toml"):
        raise ValueError("report was produced under a different configuration")
    low, high = cfg["gate"]
    forms = list(report["prompts"])
    body = {"complete": report["complete"], "gate": cfg["gate"],
            "reader_code_sha256": {name: text_digest(Path(__file__).with_name(name)) for name in CODE},
            "interpretation": "Fresh-arm pilot on three items per set; a context reading, not a registered result.",
            "forms": {form: {} for form in forms}}
    for form in forms:
        pooled, pooled_control = [], []
        for name, block in report["sets"].items():
            scores, controls = [], []
            for item in block["items"]:
                stored = item["forms"][form]
                score = best_over_answers(stored["prediction"], item["answers"])
                control = best_over_answers(stored["no_context"]["prediction"], item["answers"])
                if abs(stored["qa_f1"] - score) > 1e-12 or abs(stored["no_context"]["qa_f1"] - control) > 1e-12:
                    raise ValueError("stored score differs from the recomputed one")
                scores.append(score)
                controls.append(control)
            pooled += scores
            pooled_control += controls
            body["forms"][form][name] = {
                "n": len(scores), "per_item": scores, "median_qa_f1": statistics.median(scores),
                "mean_qa_f1": float(np.mean(scores)), "no_context_median_qa_f1": statistics.median(controls),
                "within_gate": bool(low <= statistics.median(scores) <= high) if report["complete"] else None,
                "generated_tokens": [it["forms"][form]["generated_tokens"] for it in block["items"]],
                "at_cap": sum(it["forms"][form]["generated_tokens"] >= cfg["max_new_tokens"] for it in block["items"])}
        body["forms"][form]["pooled"] = {"n": len(pooled), "median_qa_f1": statistics.median(pooled),
                                         "mean_qa_f1": float(np.mean(pooled)),
                                         "no_context_median_qa_f1": statistics.median(pooled_control)}
    write(Path(output) / "summary.json", body)
    return body


def main():
    parser = argparse.ArgumentParser(description="Benchmark control pilot (fresh arm only)")
    action = parser.add_mutually_exclusive_group(required=True)
    for name in ("table", "run", "summarize"):
        action.add_argument(f"--{name}", action="store_true")
    parser.add_argument("--config", type=Path, default=ROOT / "config/benchmark-control-pilot.toml")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    cfg = tomllib.loads(Path(args.config).read_text(encoding="utf-8"))
    if args.table:
        table_only(args, cfg)
    elif args.run:
        run(args, cfg)
    else:
        print(json.dumps(summarize(args.output), indent=1))


if __name__ == "__main__":
    main()
