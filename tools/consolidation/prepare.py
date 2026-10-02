# Restore exact prompt text from verified archives, then align each model's tokenizer.
from pathlib import Path
import hashlib
import json
import tomllib
import numpy as np
from transformers import AutoTokenizer
from linear_ceiling.e9_align import matching_pairs

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path.home() / "Desktop/Carryover-evidence"
OUT = EVIDENCE / "a100/inputs"
OUT.mkdir(parents=True, exist_ok=True)
cfg = tomllib.loads((ROOT / "config/consolidation.toml").read_text())
old = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B", revision="c1899de289a04d12100db370d81485cdf75e47ca")
sha = lambda b: hashlib.sha256(b).hexdigest()
texts = []
for cohort in ["e9s", "e9l"]:
    folder = EVIDENCE / "archive/records" / cohort
    report = json.loads((folder / "report.json").read_text())
    for hid, record in report["scores"].items():
        path = folder / "align" / record["score_file"]
        alignment = json.loads(path.read_text())
        with np.load(path.with_suffix(".npz")) as a:
            sender = old.decode(a["sender"], skip_special_tokens=False, clean_up_tokenization_spaces=False)
            receiver = old.decode(a["receiver"], skip_special_tokens=False, clean_up_tokenization_spaces=False)
            assert old.encode(sender, add_special_tokens=False) == a["sender"].tolist()
            assert old.encode(receiver, add_special_tokens=False) == a["receiver"].tolist()
        assert sha((sender+"\0"+receiver).encode()) == alignment["text_sha256"], hid
        texts.append({"handoff": hid, "cohort": cohort, "sender": sender, "receiver": receiver,
                      "text_sha256": alignment["text_sha256"], "original_sender_tokens": alignment["n_sender"]})
(OUT / "texts.jsonl").write_text("".join(json.dumps(x)+"\n" for x in texts))
manifest = {"config_sha256": sha((ROOT / "config/consolidation.toml").read_bytes()),
            "texts_sha256": sha((OUT / "texts.jsonl").read_bytes()), "models": {}}
for model in cfg["models"]:
    tok = AutoTokenizer.from_pretrained(model["model"], revision=model["revision"])
    selected = texts
    if model["name"] == "qwen17_bridge":
        selected = []
        for cohort in ["e9s", "e9l"]:
            group = sorted([t for t in texts if t["cohort"] == cohort], key=lambda t:(t["original_sender_tokens"],t["handoff"]))
            selected.extend(group[i] for i in [0,len(group)//2,len(group)-1])
    folder = OUT / model["name"]
    folder.mkdir(exist_ok=True)
    records = []
    for i, text in enumerate(selected):
        s = np.array(tok.encode(text["sender"], add_special_tokens=False), dtype=np.int64)
        r = np.array(tok.encode(text["receiver"], add_special_tokens=False), dtype=np.int64)
        record = {k:text[k] for k in ["handoff","cohort","text_sha256"]}
        record.update(sender_tokens=len(s), receiver_tokens=len(r), excluded=max(len(s),len(r))>cfg["context_cap"])
        if not record["excluded"]:
            pairs = matching_pairs(s.tolist(), r.tolist())
            assert len(pairs) > 0
            filename = f"{i:03d}.npz"
            np.savez_compressed(folder / filename, sender=s, receiver=r, pairs=pairs)
            record.update(file=f"{model['name']}/{filename}", sha256=sha((folder / filename).read_bytes()), matched_tokens=len(pairs))
        records.append(record)
        print(model["name"],i+1,len(selected),len(s),len(r),"excluded" if record["excluded"] else "aligned",flush=True)
    records.sort(key=lambda x:(x["sender_tokens"],x["handoff"]))
    manifest["models"][model["name"]] = records
(ROOT / "config/consolidation-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("Prepared",len(texts),"exact, hash-matching original prompt pairs",flush=True)
