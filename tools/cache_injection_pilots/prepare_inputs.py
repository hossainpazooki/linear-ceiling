from pathlib import Path

root = Path(__file__).parent / "records"
for name in ("report.json", "source.json", "align"):
    target = root / name
    source = Path("e9") / name
    if target.is_symlink() and target.readlink() == source:
        continue
    # An unexpected existing file or directory must survive a setup rerun.
    target.symlink_to(source, target_is_directory=name == "align")
print("Prepared root paths used by the follow-up scripts.")
