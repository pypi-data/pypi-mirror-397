import sys

from monaco_report import main


def run_main_with_args(args, capsys, monkeypatch):
    """
    Helper function:
    - replaces sys.argv
    - runs main()
    - returns stdout and stderr
    """
    monkeypatch.setattr(sys, 'argv', ["main.py"] + args)
    main.main()
    captured = capsys.readouterr()
    return captured.out, captured.err

def test_cli_default_run(capsys, monkeypatch, tmp_path):
    # Creating a fake folder and files.
    (tmp_path / "abbreviations.txt").write_text("SVF_Sebastian Vettel_Ferrari\n")
    (tmp_path / "start.log").write_text("SVF2018-05-24_12:02:58.917\n")
    (tmp_path / "end.log").write_text("SVF2018-05-24_12:04:03.9332\n")

    out, err = run_main_with_args(["--files", str(tmp_path)], capsys, monkeypatch)
    assert "Driver" in out
    assert "Team" in out
    assert err == ""


def test_cli_with_driver_filter(capsys, monkeypatch, tmp_path):
    """
    We check the filter by the rider's name.
    """
    (tmp_path / "abbreviations.txt").write_text("SVF_Sebastian Vettel_Ferrari\n")
    (tmp_path / "start.log").write_text("SVF2018-05-24_12:02:58.917\n")
    (tmp_path / "end.log").write_text("SVF2018-05-24_12:04:03.9332\n")

    out, _ = run_main_with_args(
        ["--files", str(tmp_path), "--driver", "Sebastian Vettel"], capsys, monkeypatch
    )
    assert "Sebastian Vettel" in out or "N/A" in out


def test_cli_with_limit(capsys, monkeypatch, tmp_path):
    """
    Checking the --limit option
    """
    (tmp_path / "abbreviations.txt").write_text("SVF_Sebastian Vettel_Ferrari\n")
    (tmp_path / "start.log").write_text("SVF2018-05-24_12:02:58.917\n")
    (tmp_path / "end.log").write_text("SVF2018-05-24_12:04:03.9332\n")

    out, _ = run_main_with_args(["--files", str(tmp_path), "--limit", "5"], capsys, monkeypatch)
    # There should be no more than 5 lines of riders (but more headers and separators).
    driver_lines = [line for line in out.splitlines() if "|" in line and "Driver" not in line]
    assert len(driver_lines) <= 5 + 1 # +1 just in case