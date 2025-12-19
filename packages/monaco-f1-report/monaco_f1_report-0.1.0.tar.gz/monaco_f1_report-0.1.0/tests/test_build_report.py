from datetime import datetime
from unittest.mock import patch
from monaco_report import RecordData


def make_record(abbr, driver, team, start, stop, errors=None):
    r = RecordData(abbr, driver, team, start, stop)
    if errors:
        r.errors.extend(errors)
    return r


def test_build_report_basic():
    fake_records = {
        "AAA": make_record("AAA", "Driver1", "Team1",
                           datetime(2018, 1, 1, 10, 0, 0),
                           datetime(2018, 1, 1, 10, 1, 0)),
        "BBB": make_record("BBB", "Driver2", "Team2",
                           datetime(2018, 1, 1, 10, 2, 0),
                           datetime(2018, 1, 1, 10, 3, 0)),
    }

    with (
        patch.object(RecordData, "_read_abbreviation", return_value=fake_records),
        patch.object(RecordData, "_read_start_stop", side_effect=[fake_records, fake_records]),
    ):
        cd = RecordData()
        good, bad = cd.build_report()
        assert len(good) == 2
        assert len(bad) == 0
        assert good[0].duration <= good[1].duration


def test_build_report_with_driver_filter():
    fake_records = {
        "AAA": make_record("AAA", "Driver1", "Team1",
                           datetime(2018, 1, 1, 10, 0, 0),
                           datetime(2018, 1, 1, 10, 1, 0)),
        "BBB": make_record("BBB", "Driver2", "Team2",
                           datetime(2018, 1, 1, 10, 2, 0),
                           datetime(2018, 1, 1, 10, 3, 0)),
    }

    with (
        patch.object(RecordData, "_read_abbreviation", return_value=fake_records),
        patch.object(RecordData, "_read_start_stop", side_effect=[fake_records, fake_records])
    ):
        cd = RecordData()
        good, bad = cd.build_report(driver="driver1")
        assert len(good) == 1
        assert good[0].driver.lower() == "driver1"
        assert len(bad) == 0


def test_build_report_with_errors():
    fake_records = {
        "AAA": make_record("AAA", "Driver1", "Team1",
                           datetime(2018, 1, 1, 10, 0, 0),
                           datetime(2018, 1, 1, 10, 1, 0)),
        "BBB": make_record("BBB", None, None, None, None,
                           errors=["Invalid format"]),
    }

    with (
        patch.object(RecordData, "_read_abbreviation", return_value=fake_records),
        patch.object(RecordData, "_read_start_stop", side_effect=[fake_records, fake_records])
    ):
        cd = RecordData()
        good, bad = cd.build_report()
        assert len(good) == 1
        assert len(bad) == 1
        assert "Invalid format" in bad[0].errors

