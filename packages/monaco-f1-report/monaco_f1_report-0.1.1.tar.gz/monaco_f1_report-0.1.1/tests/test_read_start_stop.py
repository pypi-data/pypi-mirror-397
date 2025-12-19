from pathlib import Path
from datetime import datetime

from monaco_report import RecordData

def write_file(tmp_path, filename, content):
    file_path = tmp_path / filename
    file_path.write_text(content, encoding="utf-8")
    return file_path

def test_read_start_stop_valid(tmp_path):
    """Test to check correct reading of start/stop times"""
    # Example of valid strings
    start_content = """\
    SVF2018-05-24_12:02:58.917
    SVM2018-05-24_12:18:37.735
"""
    # Write the starts.log file to a temporary folder
    write_file(tmp_path, "start.log", start_content)

    # Empty dictionary for entries
    records = {}

    cd = RecordData()

    # Call the method to read the start and stop
    records = cd._read_start_stop(records, tmp_path, Path("start.log"), start=True)

    # Check that the keys were read
    assert "SVF" in records
    assert "SVM" in records

    # Check that the start field is a datetime and the value is correct
    assert isinstance(records["SVF"].start, datetime)
    assert records["SVF"].start == datetime.strptime(
        "2018-05-24_12:02:58.917",
        "%Y-%m-%d_%H:%M:%S.%f")


def test_read_start_stop_invalid(tmp_path):
    """Test for checking invalid lines and error handling"""
    bad_content = """\
    XYZ2018-05-24_12:14:12
    BADLINE
    """

    write_file(tmp_path, "bad.log", bad_content)

    records = {}
    cd = RecordData()
    records = cd._read_start_stop(records, tmp_path, Path("bad.log"), start=True)

    # Check that the 3-letter keys appear in the dictionary
    assert "XYZ" in records
    assert "BAD" in records


def test_read_start_stop_stop_time(tmp_path):
    """Test to check stop time"""
    stop_content = """\
    DRR2018-05-24_13:14:12.654
"""
    write_file(tmp_path, "end.log", stop_content)

    records = {"DRR": RecordData(abbr="DRR")}  # starting blank

    cd = RecordData()
    records = cd._read_start_stop(records, tmp_path, Path("end.log"), start=False)

    # Check that stop is written correctly
    assert "DRR" in records
    assert isinstance(records["DRR"].stop, datetime)
    assert records["DRR"].stop == datetime.strptime("2018-05-24_13:14:12.654", '%Y-%m-%d_%H:%M:%S.%f')

