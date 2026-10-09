import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
TEX = (ROOT / "paper" / "paper.tex").read_text(encoding="utf-8")
EXT = json.loads((ROOT / "reports" / "post-release-extensions.json").read_text())
REG = json.loads((ROOT / "reports" / "v0.1-climate-twin-frankfurt-registry.json").read_text())


def test_variable_gaps_in_paper_match_the_extensions_file():
    for variable in ("TMK", "TNK", "TXK"):
        assert f"{EXT['variables'][variable]['mean_gap']:+.3f}" in TEX, variable


def test_relocation_steps_in_paper_match_the_extensions_file():
    for variable in ("TMK", "TNK", "TXK"):
        for step in EXT["relocation_steps"][variable].values():
            d = step["difference_after_minus_before"]
            assert (
                f"{d:.3f}".replace("-", "$-$") in TEX
                or f"{d:+.3f}" in TEX
                or f"{abs(d):.3f}" in TEX
            ), d


def test_segment_means_and_step_regression_in_paper():
    seg = EXT["variables"]["TMK"]["segment_means"]
    for s in seg.values():
        assert f"{s['mean']:.3f}" in TEX
    reg = EXT["variables"]["TMK"]["step_adjusted_trend"]
    assert f"{reg['step_2009']['estimate']:.3f}" in TEX
    assert f"{reg['slope_per_year']['estimate']:.4f}" in TEX


def test_frozen_headline_numbers_in_paper():
    assert f"{REG['mean_gap']['mean']:.3f}" in TEX if "mean_gap" in REG else "0.455" in TEX
