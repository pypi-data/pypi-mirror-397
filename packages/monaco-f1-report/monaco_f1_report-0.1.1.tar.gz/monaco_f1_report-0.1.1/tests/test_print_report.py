import pytest
from datetime import timedelta
from monaco_report import RecordData

@pytest.fixture
def good_records():
    """# Fake test entries"""
    record1 = RecordData(
        abbr="SVF",
        driver="Sebastian Vettel",
        team="Ferrari",
        start=None,
        stop=None
    )
    record1._duration = timedelta(minutes=62)

    record2 = RecordData(
        abbr="LHM",
        driver="Lewis Hamilton",
        team="Mercedes",
        start=None,
        stop=None
    )
    record2._duration = timedelta(minutes=63)

    return [record1, record2]

@pytest.fixture
def bad_records():
    record = RecordData(
        abbr="MSC",
        driver="Michael Schumacher",
        team="Ferrari",
        start=None,
        stop=None
    )
    record.errors.append("Missing start time")

    return [record]

def test_print_good_record(good_records):
    """Test for good records"""
    result = RecordData.print_report(good_records)
    assert "Sebastian Vettel" in result
    assert "Lewis Hamilton" in result


def test_print_bad_record(bad_records):
    """Test for erroneous entries"""
    result = RecordData.print_report([], bad_records)
    assert "Invalid records:" in result
    assert "MSC: Missing start time" in result


def test_unserline_length(good_records):
    """Line Counting and Underline Test"""
    result = RecordData.print_report(good_records)
    lines = result.split("\n")
    header = lines[0]
    underline = lines[1]
    assert len(header) == len(underline) # check that underline is equal to the length of the title