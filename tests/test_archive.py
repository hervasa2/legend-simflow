from __future__ import annotations

import tarfile

from legendsimflow.archive import create_plots_tarball


def test_creates_tarball(tmp_path):
    # set up generated/ with some plots dirs
    (tmp_path / "tier/stp/plots").mkdir(parents=True)
    (tmp_path / "tier/stp/plots/foo.pdf").write_text("dummy")
    (tmp_path / "tier/hit/plots").mkdir(parents=True)
    (tmp_path / "tier/hit/plots/bar.pdf").write_text("dummy")

    output = tmp_path / "tarballs" / "test-plots.tar.xz"
    create_plots_tarball(tmp_path, output, "test-plots")

    assert output.exists()
    with tarfile.open(output, "r:xz") as tar:
        names = tar.getnames()
    assert "test-plots/tier/stp/plots/foo.pdf" in names
    assert "test-plots/tier/hit/plots/bar.pdf" in names


def test_empty_tarball_when_no_plots(tmp_path):
    (tmp_path / "tier/stp").mkdir(parents=True)
    output = tmp_path / "out.tar.xz"
    create_plots_tarball(tmp_path, output, "prefix")
    assert output.exists()
    with tarfile.open(output, "r:xz") as tar:
        assert tar.getnames() == []
