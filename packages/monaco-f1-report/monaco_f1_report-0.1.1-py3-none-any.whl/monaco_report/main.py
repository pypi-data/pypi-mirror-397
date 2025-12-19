from pathlib import Path
import argparse
from importlib.resources import files

from .report import RecordData

def main():
    parser = argparse.ArgumentParser(
        description='F1 Monaco 2018 Qualification Report'
    )

    parser.add_argument(
        "--files",
        type=str,
        help="The path of the files to be processed"
    )


    parser.add_argument(
        "--asc",
        action="store_true",
        help = "Sort ascending (default)",
    )

    parser.add_argument(
        "--desc",
        action="store_true",
        help = "Sorted descending",
    )

    parser.add_argument(
        "--driver",
        type=str,
        help = "Show statistics for a specific driver",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=15,
        help = "How many entries to show in the top (default 15)",
    )

    args = parser.parse_args()

    # Sorting option.
    asc = not args.desc

    # Resolve data path
    if args.files:
        data_path = Path(args.files)
    else:
        data_path = files("monaco_report").joinpath("data")

    # Create RecordData()
    rd = RecordData()

    # Generating a report.
    good, bad = rd.build_report(
        folder=data_path,
        asc=asc,
        driver=args.driver,
    )

    # Print result.
    print(rd.print_report(good, bad, limit = args.limit))

if __name__ == '__main__':
    main()