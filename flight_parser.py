"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import argparse
from datetime import datetime
import json
import logging
import os
import sys

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "260ABB008"
FIRST_NAME = "Ece"
LAST_NAME = "Kaplan"

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Flight schedule parser and query tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", dest="input_file", help="Single input CSV file")
    group.add_argument("-d", dest="input_dir", help="Directory of CSV files")
    group.add_argument("-j", dest="json_db", help="Existing JSON database")

    parser.add_argument("-a", dest="airports_file", help="Airports list file")
    parser.add_argument("-o", dest="output_db", help="Output JSON database path")
    parser.add_argument("-q", dest="query_file", help="Query JSON file")
    parser.add_argument("-r", dest="response_dir", default=".", help="Response output folder")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    # TODO: parse arguments with argparse (-i, -d, -j, -a, -o, -q, -r).
    # TODO: load or parse the data, write the database and errors.log.
    # TODO: run the queries and write the response file.
    # Remember: remove and close the logging handler before returning,
    # also when returning early because of an error (use try/finally).
    
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    if (args.input_file or args.input_dir) and not args.airports_file:
        try:
            parser.error("-a is required when using -i or -d")
        except SystemExit as exc:
            return exc.code if isinstance(exc.code, int) else 2

    if args.json_db and args.output_db is not None:
        try:
            parser.error("-o cannot be used with -j")
        except SystemExit as exc:
            return exc.code if isinstance(exc.code, int) else 2

    db: list[dict] = []

    if args.json_db:
        if not os.path.isfile(args.json_db):
            print(f"Error: file not found: {args.json_db}", file=sys.stderr)
            return 1
        try:
            with open(args.json_db, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Error: cannot read JSON database: {exc}", file=sys.stderr)
            return 1

        if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
            print("Error: JSON database must be a list of objects", file=sys.stderr)
            return 1
        db = data
    else:
        csv_paths: list[str] = []
        if args.input_file:
            if not os.path.isfile(args.input_file):
                print(f"Error: file not found: {args.input_file}", file=sys.stderr)
                return 1
            csv_paths = [args.input_file]
        elif args.input_dir:
            if not os.path.isdir(args.input_dir):
                print(f"Error: directory not found: {args.input_dir}", file=sys.stderr)
                return 1
            try:
                filenames = sorted(os.listdir(args.input_dir))
            except OSError as exc:
                print(f"Error: cannot read directory: {exc}", file=sys.stderr)
                return 1
            for name in filenames:
                full_path = os.path.join(args.input_dir, name)
                if name.endswith(".csv") and os.path.isfile(full_path):
                    csv_paths.append(full_path)
            if not csv_paths:
                print(f"Error: no .csv files found in {args.input_dir}", file=sys.stderr)
                return 1

        if not os.path.isfile(args.airports_file):
            print(f"Error: airports file not found: {args.airports_file}", file=sys.stderr)
            return 1

        try:
            airports = load_airports(args.airports_file)
        except OSError as exc:
            print(f"Error: cannot read airports file: {exc}", file=sys.stderr)
            return 1

        db_path = args.output_db if args.output_db is not None else "db.json"
        log_dir = os.path.dirname(os.path.abspath(db_path))
        log_path = os.path.join(log_dir, "errors.log")

        logger = logging.getLogger("flight_parser")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        handler: logging.FileHandler | None = None

        try:
            handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            logger.addHandler(handler)

            records, errors = parse_files(csv_paths, airports)
            for err in errors:
                logger.warning(err)

            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)

            db = records
        except OSError as exc:
            print(f"Error: file error during parsing: {exc}", file=sys.stderr)
            return 1
        finally:
            if handler is not None:
                logger.removeHandler(handler)
                handler.close()

    if args.query_file:
        if not os.path.isfile(args.query_file):
            print(f"Error: query file not found: {args.query_file}", file=sys.stderr)
            return 1
        try:
            with open(args.query_file, "r", encoding="utf-8") as f:
                queries = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Error: invalid query JSON file: {exc}", file=sys.stderr)
            return 1

        if not isinstance(queries, (dict, list)):
            print("Error: query file must contain an object or a list", file=sys.stderr)
            return 1

        responses = run_queries(db, queries)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp}.json"
        out_path = os.path.join(args.response_dir, filename)

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(responses, f, indent=2)
        except OSError as exc:
            print(f"Error: cannot write response file: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
    