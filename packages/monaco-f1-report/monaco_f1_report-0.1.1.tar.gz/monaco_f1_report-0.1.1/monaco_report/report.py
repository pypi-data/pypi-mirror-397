from datetime import datetime
from pathlib import Path
from importlib.resources import files

import re


class RecordData:
    def __init__(
            self,
            abbr: str = None,
            driver: str = None,
            team: str = None,
            start: datetime = None,
            stop: datetime = None,
    ):
        """
        Represents a single Formula 1 record.
        Parameters
        ----------
        abbr : str, optional
            Abbreviation of the driver (e.g. 'SVF' for Sebastian Vettel).
        driver : str, optional
            Full driver name.
        team : str, optional
            Team name.
        start : datetime, optional
            Start time of the lap.
        stop : datetime, optional
            Stop time of the lap.
        """
        self.abbr = abbr
        self.driver = driver
        self.team = team
        self.start = start
        self.stop = stop
        self.errors: list[str] = []


    def __str__(self):
        driver = self.driver or "N/A"
        team = self.team or "N/A"
        time_str = str(self.duration) if self.duration else "N/A"
        return f"{driver:<20} | {team:<20} | {time_str:>20}"


    @property
    def duration(self):
        """Calculate lap duration if start and stop are valid.
    Returns
    -------
    timedelta | None
        Duration between stop and start. Returns None if validation fails."""
        # Check if not start stop added in errors.
        if not self.start or not self.stop:
            return None
        # Check if start >= stop added in errors.
        if self.start >= self.stop:
            return None
        return self.stop - self.start


    @classmethod
    def _read_abbreviation(
            cls,
            folder: Path,
            file: Path,
    ) -> dict[str, 'RecordData']:
        """
        Read abbreviation file and create initial RecordData objects.
        Parameters
        ----------
        folder : Path
            Path to the data directory.
        file : Path
            Abbreviation file name (e.g. "abbreviations.txt").

        Returns
        -------
        dict[str, RecordData]
            Dictionary mapping abbreviation -> RecordData.
        """

        # Create empty dictionary.
        records = {}

        # Check for folder existence
        if not folder.exists() or not folder.is_dir():
            raise FileNotFoundError(f"Folder '{folder}' does not exist.")

        # Forming a full file path.
        file_path = folder / file

        # Check for file existence
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"File '{file_path}' does not exist.")

        # Regular expression to extract abbreviation, name, and command from a string.
        pattern = re.compile(r'^(?P<abbr>[A-Z]{3})_(?P<driver>[^_]+)_(?P<team>.+$)')

        # Read file
        with open(file_path, encoding="utf-8") as f:
            # We go through each line with its number.
            for lineno, line in enumerate(f, 1):
                # Remove spaces from the beginning and end
                line = line.strip()
                if not line:
                    continue # Skipping blank lines.

                math = pattern.match(line) # Compare the string with the pattern

                if math:
                    # If a match is found, we get data from the named groups.
                    abbr = math.group('abbr')
                    driver = math.group('driver').strip()
                    team = math.group('team').strip()

                    # Create a RecordData object and add it to the dictionary.
                    records[abbr] = cls(abbr=abbr, driver=driver, team=team)

                else:
                    # If the format is incorrect — create an empty object with an error.
                    record = cls()
                    record.errors.append(f"[Line {lineno}] Invalid format: '{line}'")
                    records[line[:3]] = record # Add an entry to the dictionary with the key — the first 3.

        return records # Return all read records.


    def _read_start_stop(
            self,
            records_dict: dict[str, 'RecordData'],
            folder: Path,
            file: Path,
            start: bool = True
    ) -> dict[str, 'RecordData']:
        """
        Read start or stop time logs and update existing records.

        Parameters
        ----------
        records_dict : dict[str, RecordData]
            Dictionary of records to be updated.
        folder : Path
            Path to the data directory.
        file : Path
            Log file name (e.g. "start.log" or "end.log").
        start : bool, default=True
            If True, updates start times, else stop times.

        Returns
        -------
        dict[str, RecordData]
            Updated records dictionary.
        """

        # Forming a full file path.
        file_path = folder / file

        # Check for file existence
        if not file_path.is_file():
            raise FileNotFoundError(f"File '{file_path}' does not exist.")

        # Create a regular expression to parse lines in a file
        # Search for three capital letters (abbr) and a date in the format 'YYYY-MM-DD_HH:MM:SS.sss...'
        pattern = re.compile(
            r'^(?P<abbr>[A-Z]{3})'
            r'(?P<time>\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}\.\d+)$'
        )

        # Read file
        with open(file_path, encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                # Cleansing a line of spaces at the beginning and end.
                line = line.strip()
                if not line:
                    continue # Skipping blank lines.

                # Compare the string with a regular expression.
                math = pattern.match(line)

                # If the string does not match the pattern
                if not math:
                    # Define the abbreviation as the first three characters of the string.
                    abbr = line[:3] if len(line) > 3 else "???"
                    # Add a new entry to the dictionary or get an existing one,
                    # and add a message about the incorrect string format
                    records_dict.setdefault(abbr, RecordData(abbr=abbr)).errors.append(
                        f"[Line {lineno}] Invalid format: '{line}'"
                    )
                    continue
                # If the string matches the pattern, we get the abbreviation.
                abbr = math.group('abbr')
                try:
                    # Parse the time from a string into a datetime object
                    time_val = datetime.strptime(math.group('time'), '%Y-%m-%d_%H:%M:%S.%f')
                except ValueError:
                    # If the time is in the wrong format, add an error message.
                    records_dict.setdefault(abbr, RecordData(abbr=abbr)).errors.append(
                        f"[Line {lineno}] Invalid datetime format: '{line}'"
                    )
                    continue

                # Get or create an entry for this abbreviation
                record = records_dict.setdefault(abbr, RecordData(abbr=abbr))

                # Depending on the start flag, we set the start or end time
                if start:
                    record.start = time_val
                else:
                    record.stop = time_val

        return records_dict


    def build_report(
            self,
            folder: Path | None = None,
            file: Path = Path("abbreviations.txt"),
            start_file: Path = Path("start.log"),
            stop_file: Path = Path("end.log"),
            asc: bool = True,
            driver: str | None = None,
    ) -> tuple[list["RecordData"], list["RecordData"]]:
        """
         Build a race report from raw log files.
    Parameters
    ----------
    folder : Path, default="../data"
        Path to the directory with log files.
    file : Path, default="abbreviations.txt"
        Abbreviations file.
    start_file : Path, default="start.log"
        File with start times.
    stop_file : Path, default="end.log"
        File with stop times.
    asc : bool, default=True
        Sort ascending (fastest first if False).
    driver : str | None, optional
        Filter by driver name (case-insensitive).

    Returns
    -------
    tuple[list[RecordData], list[RecordData]]
        Two lists: (valid records, invalid/problematic records).
        """
        # Resolve data folder
        if folder is None:
            folder = files("monaco_report").joinpath("data")

        # Read abbreviations.txt
        records_dict = self._read_abbreviation(folder, file)
        # Read the start data.
        records_dict = self._read_start_stop(records_dict, folder, start_file, start=True)
        # Reading the stop data
        records_dict = self._read_start_stop(records_dict, folder, stop_file, start=False)

        # Create two lists for good and bad records.
        good_records: list[RecordData] = []
        bad_records: list[RecordData] = []

        # Validation for @property duration.
        for record in records_dict.values():
            if not record.start or not record.stop:
                record.errors.append("Missing start or stop time.")
            elif record.start >= record.stop:
                record.errors.append("Start time is after or equal to stop time.")

            if record.errors:
                bad_records.append(record)
            else:
                good_records.append(record)

        # Good_records sorted for duration.
        good_records = sorted(
            good_records,
            key=lambda r: r.duration,
            reverse=not asc
        )

        # Filter by driver name, if passed.
        if driver:
            good_records = [
                r for r in good_records
                if r.driver and driver.lower() in r.driver.lower()]
        return good_records, bad_records

    @staticmethod
    def print_report(
            good_records: list["RecordData"],
            bad_records: list["RecordData"] | None = None,
            limit: int = 15
    ) -> str:
        """
         Generate a textual race report.

        Parameters
        ----------
        good_records : list[RecordData]
            List of valid race records.
        bad_records : list[RecordData], optional
            List of invalid/problematic records. Default None.
        limit : int, default=15
            Maximum number of valid records to display.

        Returns
        -------
        str
            Formatted text table with race results and errors.
        """
        # Forming the title.
        header = f"{'Driver':<20} | {'Team':<20} | {'Time':>20}"

        # Set underline to the length of the title.
        underline = len(header)

        # list of lines that we will gradually collect.
        lines: list[str] = []

        # Table header.

        lines.append(header) # add a title
        lines.append("-" * underline) # add a dividing line

        # Output the first 15 good_records.
        for record in good_records[:limit]:
            # If there is no driver or team name, substitute "N/A"
            driver = record.driver or "N/A"
            team = record.team or "N/A"

            # If duration is present — formatted time, otherwise "N/A"
            if record.duration:
                time_str = str(record.duration)
            else:
                time_str = "N/A"

            # Add the formatted row to the table.
            lines.append(f"{driver:<20} | {team:<20} | {time_str:>20}")

        # If there are problem records, output another block
        if bad_records:
            lines.append("Invalid records:") # error header
            for record in bad_records:
                # If there is an abbreviation, show it, otherwise UNKNOWN.
                abbr = record.abbr or "UNKNOWN"

                # Print all errors that have been accumulated in record.errors.
                for err in record.errors:
                    lines.append(f"{abbr}: {err}")

        # Combine all lines into one text with line breaks
        return "\n".join(lines)
