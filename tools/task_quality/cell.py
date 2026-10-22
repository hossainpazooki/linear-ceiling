# Task-quality cell driver (ruling C of the 2026-10-13 plan): structured-field recall under the
# cache-behavior arms. Per handoff the receiver's cache for R is built FRESH (its own prefill), by
# REUSE of the sender's matched states relocated to R (0047's REUSE-ALL), by the RANDOM norm-matched
# perturbation of the fresh states (0047's control), and by REPAIR at each registered budget (the
# top-f matched tokens by archived token-mean delta_K recomputed in place, 0061's ORACLE-f). Under
# each cache every drawn item's question is appended after R and answered by greedy decoding; the
# field is read by the registered scorer. The continuation is not scored and no KL is measured.
import argparse
import gc
import json
import os
import platform
import subprocess
import time
import tomllib
from pathlib import Path

import numpy as np

from linear_ceiling.e7_stats import quantile, summary as handoff_summary
from linear_ceiling.e9_pertoken import centered_delta, token_mean
from linear_ceiling.rng import make_rng
from .items import KINDS, alignment_file, canonical_contains, contains, exact_match, first_span_exact, token_f1
from .pilot import (FORM2_KINDS, ROOT, digest, drawn_items, form2_count, greedy_answer, load_model,
                    load_tokenizer, question_for, same_text, text_digest, write)

CODE = ("cell.py", "pilot.py", "items.py")
SCORERS = ("exact_match", "contains", "token_f1", "first_span_exact", "canonical_contains")


def scores_for(prediction, gold, kind):
    return {"exact_match": exact_match(prediction, gold), "contains": contains(prediction, gold),
            "token_f1": token_f1(prediction, gold), "first_span_exact": first_span_exact(prediction, gold, kind),
            "canonical_contains": canonical_contains(prediction, gold)}


def arm_list(cfg):
    # (label, repair fraction); labels never round the fraction.
    arms = [("fresh", 0), ("reuse", 0), ("random", 0)] + [(f"repair_{f * 100:g}pct", f) for f in cfg["repair_fractions"]]
    if any(not 0 < f <= 1 for f in cfg["repair_fractions"]) or len({a for a, _ in arms}) != len(arms):
        raise ValueError("repair fractions must be in (0, 1] with distinct labels")
    return arms


def cell_handoffs(items_body, floor):
    """Handoffs at or above the item floor, largest sender first (the memory probe, as 0047); the
    void handoffs by id."""
    kept = sorted((h for h in items_body["handoffs"] if form2_count(h) >= floor),
                  key=lambda h: (-h["n_sender"], h["handoff"]))
    void = [h["handoff"] for h in items_body["handoffs"] if form2_count(h) < floor]
    return kept, void


def load_archive(archive, archived_report, row):
    """sender, receiver, pairs and the archived token-mean delta_K of one handoff, every file checked
    against the hash the items file or the archive report pins."""
    hid = row["handoff"]
    alignment = alignment_file(archive / "align", hid)
    if digest(alignment) != row["alignment_sha256"]:
        raise ValueError(f"alignment file differs from the items file's pin: {hid}")
    score = archived_report["scores"][hid]
    score_path, token_path = archive / "scores" / score["score_file"], archive / "tokens" / score["tokens_file"]
    if digest(score_path) != score["score_sha256"] or digest(token_path) != score["tokens_sha256"]:
        raise ValueError(f"archive hash mismatch: {hid}")
    with np.load(alignment, allow_pickle=False) as arrays:
        sender, receiver, pairs = (arrays[key] for key in ("sender", "receiver", "pairs"))
    body = json.loads(score_path.read_text(encoding="utf-8"))
    with np.load(token_path, allow_pickle=False) as tokens:
        delta = centered_delta(tokens["same_K"], np.array([r["sst"] for r in body["same"]["K"]]), len(pairs))
    shas = {"alignment_sha256": row["alignment_sha256"], "score_sha256": score["score_sha256"],
            "tokens_sha256": score["tokens_sha256"]}
    return sender, receiver, pairs, token_mean(delta), shas


def score_items(model, tokenizer, cache, prefix_length, questions, cfg, stop_ids):
    """Every drawn item under every registered prompt form against one cache; the cache is returned
    to the receiver prefix after each decode."""
    out = []
    for item, question in questions:
        forms = {}
        for form in cfg["forms"]:
            wrapper = cfg["prompts"][form]
            question_ids = tokenizer.encode(wrapper["before"] + question + wrapper["after"], add_special_tokens=False)
            started = time.perf_counter()
            generated = greedy_answer(model, tokenizer, cache, prefix_length, question_ids,
                                      cfg["max_new_tokens"], stop_ids, cfg["stop_at_newline"])
            prediction = tokenizer.decode(generated)
            forms[form] = {"prediction": prediction, "generated_tokens": len(generated),
                           "seconds": time.perf_counter() - started, **scores_for(prediction, item["answer"], item["kind"])}
        out.append(forms)
    return out


def identity_of(cfg, args, device):
    import torch
    import transformers
    cell = cfg["cells"][args.cell]
    body = {"config_sha256": text_digest(args.config), "cell": args.cell, "items_sha256": cell["items_sha256"],
            "code_sha256": {name: text_digest(Path(__file__).with_name(name)) for name in CODE},
            "model": cfg["model"], "model_revision": cfg["revision"], "transformers": transformers.__version__,
            "torch": torch.__version__, "device": str(device), "dtype": "float32",
            "machine": platform.machine(), "system": platform.system()}
    if device.type == "cuda":
        body.update(gpu=torch.cuda.get_device_name(device), cuda=torch.version.cuda,
                    cublas_workspace_config=os.environ.get("CUBLAS_WORKSPACE_CONFIG"))
    return body


def run(args, cfg):
    import torch
    from tools.cache_behavior.core import construct, matched, prefill, random_candidate, relocated_candidate, validate_pairs
    cell = cfg["cells"][args.cell]
    items_path, archive = ROOT / cell["items_file"], ROOT / cell["archive"]
    if not same_text(cell["items_sha256"], items_path):
        raise ValueError("items file differs from the registered sha")
    items_body = json.loads(items_path.read_text(encoding="utf-8"))
    archived_report = json.loads((archive / "report.json").read_text(encoding="utf-8"))
    if not archived_report["complete"]:
        raise ValueError("the alignment archive is incomplete")
    arms = arm_list(cfg)
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    device = torch.device(args.device)
    if device.type == "cuda":
        torch.use_deterministic_algorithms(True)
    tokenizer = load_tokenizer(cfg)
    model = load_model(cfg, device)
    freq = model.model.rotary_emb.inv_freq.detach().cpu()
    stop_ids = {tokenizer.eos_token_id, tokenizer.convert_tokens_to_ids("<|endoftext|>")}
    identity = identity_of(cfg, args, device)
    args.output.mkdir(parents=True, exist_ok=True)
    report_path = args.output / "report.json"
    kept, void = cell_handoffs(items_body, cfg["min_form2_items"])
    if report_path.exists():
        if not args.resume:
            raise ValueError("output exists; pass --resume to verify and continue")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report["identity"] != identity:
            raise ValueError("resume identity differs (code, items, configuration, runtime, or device)")
        summarize(args.output)
    else:
        report = {"identity": identity,
                  "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  "rope": model.config.rope_parameters, "arms": [a for a, _ in arms], "forms": cfg["forms"],
                  "prompts": cfg["prompts"], "questions": cfg["questions"], "floor": cfg["min_form2_items"],
                  "run_order": [h["handoff"] for h in kept], "void": void, "handoffs": {}, "complete": False}
        write(report_path, report)
    for index, row in enumerate(kept[:1] if args.probe else kept):
        hid = row["handoff"]
        if hid in report["handoffs"]:
            continue
        sender, receiver, pairs, delta_mean, shas = load_archive(archive, archived_report, row)
        validate_pairs(sender, receiver, pairs)
        if len(receiver) != row["n_receiver"]:
            raise ValueError(f"receiver length differs from the items file: {hid}")
        questions = [(item, question_for(item, cfg)) for item in drawn_items(row, cfg, index)]
        if device.type == "cuda":
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats(device)
        started = time.perf_counter()
        cache = prefill(model, receiver, cfg["chunk_tokens"])
        assembly = {"fresh": {"copied": 0, "recomputed": len(receiver), "assembly_seconds": time.perf_counter() - started}}
        fresh_states = matched(cache, pairs[:, 1])
        results = {"fresh": score_items(model, tokenizer, cache, len(receiver), questions, cfg, stop_ids)}
        del cache
        sender_cache = prefill(model, sender, cfg["chunk_tokens"])
        source = matched(sender_cache, pairs[:, 0])
        del sender_cache
        reused = relocated_candidate(source, pairs, freq)
        for arm, fraction in arms[1:]:
            candidate, removed = reused, []
            if arm == "random":
                candidate = random_candidate(fresh_states, reused, make_rng(cfg["seed"] + index))
            elif arm.startswith("repair_"):
                removed = np.argsort(-delta_mean, kind="stable")[:int(np.ceil(len(pairs) * fraction))]
            cache, assembly[arm] = construct(model, receiver, pairs, candidate, cfg["chunk_tokens"], removed)
            results[arm] = score_items(model, tokenizer, cache, len(receiver), questions, cfg, stop_ids)
            del cache, candidate
            gc.collect()
        records = []
        for position, (item, question) in enumerate(questions):
            records.append({**{key: item[key] for key in ("kind", "key", "answer", "first_token", "answer_tokens")},
                            "question": question, "arms": {arm: results[arm][position] for arm, _ in arms}})
        report["handoffs"][hid] = {"n_sender": int(len(sender)), "n_receiver": int(len(receiver)), "n_matched": int(len(pairs)),
                                   "archive": shas, "assembly": assembly, "items": records,
                                   "peak_allocated_GiB": (torch.cuda.max_memory_allocated(device) / 2**30
                                                          if device.type == "cuda" else None)}
        report["complete"] = len(report["handoffs"]) == len(report["run_order"])
        write(report_path, report)
        body = summarize(args.output)
        head = body["headline"]
        print(f"{len(report['handoffs'])}/{len(report['run_order'])} {hid}: " + " | ".join(
            f"{arm}={head['per_handoff'][arm][-1]:.3f}" for arm, _ in arms), flush=True)
        del source, reused, fresh_states


def bootstrap_median(values, resamples, seed):
    # Percentile interval of the median over handoffs, handoffs resampled with replacement.
    rng = make_rng(seed)
    values = np.asarray(values, dtype=np.float64)
    medians = [float(np.median(values[rng.integers(0, len(values), len(values))])) for _ in range(resamples)]
    return {"low": quantile(medians, 0.025), "high": quantile(medians, 0.975), "resamples": resamples}


def retention(per_handoff, arms, resamples, seed, handoff_ids=None):
    """Per arm: raw retention (arm accuracy over fresh) and the floor-normalized retention
    ((arm - random) / (fresh - random)), each per handoff, with the handoffs where the denominator
    is not positive counted as void, listed by id, and the medians over the rest."""
    out = {}
    fresh, random = np.asarray(per_handoff["fresh"]), np.asarray(per_handoff["random"])
    ids = np.asarray(handoff_ids if handoff_ids is not None else [str(i) for i in range(len(fresh))])
    for arm in arms:
        acc = np.asarray(per_handoff[arm])
        raw_ok, norm_ok = fresh > 0, fresh > random
        raw = (acc[raw_ok] / fresh[raw_ok]).tolist()
        norm = ((acc[norm_ok] - random[norm_ok]) / (fresh[norm_ok] - random[norm_ok])).tolist()
        out[arm] = {"raw": {**(handoff_summary(raw) if raw else {"n": 0}), "void": int((~raw_ok).sum()),
                            "void_handoffs": ids[~raw_ok].tolist(),
                            **({"bootstrap": bootstrap_median(raw, resamples, seed)} if raw else {})},
                    "floor_normalized": {**(handoff_summary(norm) if norm else {"n": 0}), "void": int((~norm_ok).sum()),
                                         "void_handoffs": ids[~norm_ok].tolist(),
                                         **({"bootstrap": bootstrap_median(norm, resamples, seed + 1)} if norm else {})}}
    return out


def summarize(output):
    """Fail-closed reader: every score recomputed from the stored prediction; the headline under the
    registered form, scorer and kinds; every form x scorer in the sensitivity table."""
    report = json.loads((Path(output) / "report.json").read_text(encoding="utf-8"))
    cfg = tomllib.loads((ROOT / "config/task-quality-cell.toml").read_text(encoding="utf-8"))
    if not same_text(report["identity"]["config_sha256"], ROOT / "config/task-quality-cell.toml"):
        raise ValueError("report was produced under a different configuration")
    arms, forms = report["arms"], report["forms"]
    head = cfg["headline"]
    # Recompute, then accumulate per (form, scorer, kind set) per arm per handoff.
    handoff_ids = [hid for hid in report["run_order"] if hid in report["handoffs"]]
    acc = {form: {scorer: {arm: {"form2": [], "signature": []} for arm in arms} for scorer in SCORERS} for form in forms}
    by_kind = {form: {arm: {kind: [] for kind in KINDS} for arm in arms} for form in forms}
    n_items = {"form2": [], "signature": []}
    for hid in handoff_ids:
        items = report["handoffs"][hid]["items"]
        n_items["form2"].append(sum(it["kind"] in FORM2_KINDS for it in items))
        n_items["signature"].append(sum(it["kind"] == "signature" for it in items))
        for form in forms:
            rows = {scorer: {arm: {"form2": [], "signature": []} for arm in arms} for scorer in SCORERS}
            for it in items:
                for arm in arms:
                    stored = it["arms"][arm][form]
                    scores = scores_for(stored["prediction"], it["answer"], it["kind"])
                    for scorer in SCORERS:
                        if abs(float(stored[scorer]) - float(scores[scorer])) > 1e-12:
                            raise ValueError(f"stored score differs from the recomputed one: {hid} {arm} {form} {scorer}")
                        if it["kind"] in FORM2_KINDS:
                            rows[scorer][arm]["form2"].append(float(scores[scorer]))
                        if it["kind"] == "signature":
                            rows[scorer][arm]["signature"].append(float(scores[scorer]))
                    by_kind[form][arm][it["kind"]].append(float(scores[head["scorer"]]))
            for scorer in SCORERS:
                for arm in arms:
                    for pool in ("form2", "signature"):
                        values = rows[scorer][arm][pool]
                        acc[form][scorer][arm][pool].append(float(np.mean(values)) if values else float("nan"))
    pool = "signature" if list(head["kinds"]) == ["signature"] else "form2"
    if set(head["kinds"]) not in ({"signature"}, set(FORM2_KINDS)):
        raise ValueError("headline kinds must be the signature kind or the form-2' kinds")
    per_handoff = {arm: acc[head["form"]][head["scorer"]][arm][pool] for arm in arms}
    under_floor = [hid for hid, n in zip(handoff_ids, n_items[pool]) if n < cfg["min_form2_items"]]
    body = {"complete": report["complete"], "handoffs": len(handoff_ids), "void": report["void"],
            "reader_code_sha256": {name: text_digest(Path(__file__).with_name(name)) for name in CODE},
            "interpretation": "Structured-field recall under each cache; descriptive, no band, no verdict.",
            "headline": {**head, "pool": pool, "handoff_ids": handoff_ids, "items_per_handoff": n_items[pool],
                         "under_floor": under_floor, "per_handoff": per_handoff,
                         "accuracy": {arm: {**handoff_summary(per_handoff[arm]),
                                            "bootstrap": bootstrap_median(per_handoff[arm], cfg["bootstrap_resamples"], cfg["seed"])}
                                      for arm in arms},
                         "retention": retention(per_handoff, arms, cfg["bootstrap_resamples"], cfg["seed"], handoff_ids)},
            "sensitivity": {form: {scorer: {pool_: {arm: handoff_summary(acc[form][scorer][arm][pool_])
                                                     for arm in arms} for pool_ in ("form2", "signature")}
                                   for scorer in SCORERS} for form in forms},
            "by_kind": {form: {arm: {kind: {"n": len(rows), "mean": float(np.mean(rows))}
                                     for kind, rows in by_kind[form][arm].items() if rows} for arm in arms} for form in forms},
            "assembly": {arm: {"copied": [report["handoffs"][h]["assembly"][arm]["copied"] for h in handoff_ids],
                               "recomputed": [report["handoffs"][h]["assembly"][arm]["recomputed"] for h in handoff_ids]}
                         for arm in arms}}
    write(Path(output) / "summary.json", body)
    return body


def main():
    parser = argparse.ArgumentParser(description="Task-quality cell: structured-field recall under the cache-behavior arms")
    action = parser.add_mutually_exclusive_group(required=True)
    for name in ("run", "summarize"):
        action.add_argument(f"--{name}", action="store_true")
    parser.add_argument("--config", type=Path, default=ROOT / "config/task-quality-cell.toml")
    parser.add_argument("--cell", choices=("long", "short"), default="long")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--probe", action="store_true", help="the largest sender only (R2 memory probe)")
    args = parser.parse_args()
    cfg = tomllib.loads(Path(args.config).read_text(encoding="utf-8"))
    if args.run:
        run(args, cfg)
    else:
        print(json.dumps(summarize(args.output)["headline"]["accuracy"], indent=1))


if __name__ == "__main__":
    main()
