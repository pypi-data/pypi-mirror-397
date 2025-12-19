import tempfile
from pathlib import Path
import pytest

from monaco_report import RecordData

@pytest.fixture
def temp_folder():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

def test_read_abbreviation_valid(temp_folder):
    """Verify that correctly formatted strings are parsed without errors."""
    # Create a file with two correct entries.
    test_file = temp_folder / "abbreviations.txt"
    content = (
        "DRR_Daniel Ricciardo_RED BULL RACING TAG HEUER\n"
        "LHM_Lewis Hamilton_MERCEDES\n"
    )
    test_file.write_text(content, encoding="utf-8")

    # We read the file through our function.
    records = RecordData._read_abbreviation(temp_folder, Path("abbreviations.txt"))

    # Check the first entry
    assert "DRR" in records
    assert records["DRR"].driver == "Daniel Ricciardo"
    assert records["DRR"].team == "RED BULL RACING TAG HEUER"
    assert records["DRR"].errors == [] # No errors

    # Checking the second entry
    assert "LHM" in records
    assert records["LHM"].driver == "Lewis Hamilton"


def test_read_abbreviation_invalid_line(temp_folder):
    """Verify that a string with an incorrect format (no underscores) causes an error,
     but does not break the program, and is treated as an invalid entry."""
    test_file = temp_folder / "abbreviations.txt"
    content = (
        "INVALID LINE WITHOUT UNDERSCORES\n"
        "DRR_Daniel Ricciardo_RED BULL RACING\n"
    )
    test_file.write_text(content, encoding="utf-8")

    # Reading the file
    records = RecordData._read_abbreviation(temp_folder, Path("abbreviations.txt"))

    # Invalid entry must be with key 'INV' — first 3 letters
    assert "INV" in records
    assert records["INV"].errors # There must be at least 1 error
    assert "[Line 1]" in records["INV"].errors[0] # Error must contain line number

    # Check that the second record is parsed correctly
    assert "DRR" in records
    assert not records["DRR"].errors


def test_read_abbreviation_empty_lines_skipped(temp_folder):
    """Verify that empty lines are ignored
    and do not create any records or errors."""
    test_file = temp_folder / "abbreviations.txt"
    content = "\n\nDRR_Daniel Ricciardo_RED BULL RACING\n\n"
    test_file.write_text(content, encoding="utf-8")

    records = RecordData._read_abbreviation(temp_folder, Path("abbreviations.txt"))

    # Check that DRR is parsed
    assert "DRR" in records

    # Check that no extra lines have been inserted
    assert len(records) == 1

    # Checking for errors
    assert records["DRR"].errors == []


def test_read_abbreviation_file_not_found(temp_folder):
    """Checks that a missing file is causing the error."""
    # We do not create the file intentionally
    missing_file = Path("non_existing.txt")

    with pytest.raises(FileNotFoundError) as exc_info:
        RecordData._read_abbreviation(temp_folder, missing_file)

    # Check that the message contains the desired fragment
    assert "non_existing.txt" in str(exc_info.value)
    assert "does not exist" in str(exc_info.value)


def test_read_abbreviation_folder_not_found(temp_folder):
    """Checks that a missing folder is causing the error."""
    non_existing_folder = Path("non_existing_folder.txt")
    file_name = Path("abbreviations.txt")

    with pytest.raises(FileNotFoundError) as exc_info:
        RecordData._read_abbreviation(non_existing_folder, file_name)

    assert "does not exist" in str(exc_info.value)
