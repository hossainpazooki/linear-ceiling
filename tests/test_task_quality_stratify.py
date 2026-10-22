import numpy as np
import pytest

from linear_ceiling.e9_pertoken import SEAM_BIN_LABELS
from tools.task_quality import stratify


def test_attach_seam_bins_reads_the_bin_from_the_alignment_alone():
    # Receiver of 12 tokens; matched 0..3 and 6..11 (4 and 5 are seams); first tokens at 0, 3, 8.
    pairs = np.column_stack((np.arange(10), np.array([0, 1, 2, 3, 6, 7, 8, 9, 10, 11])))
    items = [{"first_token": 0, "valid": True}, {"first_token": 3, "valid": True},
             {"first_token": 8, "valid": True}, {"first_token": 4, "valid": False}]
    out = stratify.attach_seam_bins(items, pairs, 12)
    # b = receiver positions strictly between the token and the nearest seam (4 and 5 are unmatched):
    # position 0 -> 3 (bin 2-3), position 3 -> 0 (bin 0), position 8 -> 2 (bin 2-3).
    assert [it["seam_bin"] for it in out[:3]] == [2, 0, 2]
    assert out[3]["seam_bin"] is None
    with pytest.raises(ValueError):
        stratify.attach_seam_bins([{"first_token": 4, "valid": True}], pairs, 12)


def test_stratified_draw_allocates_by_bin_share_and_is_seeded():
    items = [{"first_token": i, "seam_bin": 0 if i < 60 else (2 if i < 90 else 5)} for i in range(100)]
    drawn = stratify.stratified_draw(items, 40, 7)
    assert len(drawn) == 40 and [it["first_token"] for it in drawn] == sorted(it["first_token"] for it in drawn)
    counts = stratify.bin_counts(drawn)
    assert counts[SEAM_BIN_LABELS[0]] == 24 and counts[SEAM_BIN_LABELS[2]] == 12 and counts[SEAM_BIN_LABELS[5]] == 4
    assert stratify.stratified_draw(items, 40, 7) == drawn and stratify.stratified_draw(items, 40, 8) != drawn
    assert stratify.stratified_draw(items[:30], 40, 7) == sorted(items[:30], key=lambda it: it["first_token"])


def test_small_bins_keep_one_item_when_the_cap_allows():
    items = [{"first_token": i, "seam_bin": 0} for i in range(99)] + [{"first_token": 99, "seam_bin": 4}]
    drawn = stratify.stratified_draw(items, 10, 1)
    assert stratify.bin_counts(drawn)[SEAM_BIN_LABELS[4]] == 1 and len(drawn) == 10
