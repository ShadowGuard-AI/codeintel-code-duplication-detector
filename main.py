import argparse
import hashlib
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="Detects code duplication within a codebase.")
    parser.add_argument("path", help="Path to the codebase to analyze.")
    parser.add_argument("-m", "--min-lines", type=int, default=5,
                        help="Minimum number of lines for a code block to be considered a duplicate.")
    parser.add_argument("-r", "--report-file", type=str, default="duplication_report.txt",
                        help="Path to the report file.")
    parser.add_argument("-e", "--exclude", nargs='+', default=[],
                        help="List of file or directory names to exclude from the analysis.")
    return parser.parse_args()


def calculate_hash(code_block):
    """
    Calculates the SHA-256 hash of a code block.
    """
    try:
        return hashlib.sha256(code_block.encode('utf-8')).hexdigest()
    except Exception as e:
        logging.error(f"Error calculating hash: {e}")
        return None


def find_duplicates(path, min_lines, exclude):
    """
    Finds duplicate code blocks within the given path.
    """
    code_blocks = {}  # Hash: (filename, start_line, end_line)
    duplicates = []
    unreadable = []

    # A single file is a valid target: os.walk on a file yields
    # nothing, which used to report no duplicates for a file that was
    # never read. Collect the file list first, then scan it.
    if os.path.isfile(path):
        filepaths = [path]
    else:
        filepaths = []
        for root, _, files in os.walk(path):
            for name in files:
                filepaths.append(os.path.join(root, name))

    try:
        for filepath in filepaths:
            file = os.path.basename(filepath)
            # Exclusions are names, as the help text says: a name
            # matches the file name or any directory component of
            # its path. The old substring test on the full path
            # also skipped files whose names merely contain the
            # text, so excluding test would skip latest.py.
            parts = os.path.normpath(filepath).split(os.sep)
            if any(ex in parts for ex in exclude):
                logging.debug(f"Skipping excluded file: {filepath}")
                continue

            if not file.endswith(".py"):  # Analyze only python files (can be configurable)
                continue

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception as e:
                logging.error(f"Error reading file {filepath}: {e}")
                unreadable.append(filepath)
                continue

            for i in range(len(lines) - min_lines + 1):
                block = "".join(lines[i:i + min_lines])
                block_hash = calculate_hash(block)

                if block_hash:
                    if block_hash in code_blocks:
                        existing_file, existing_start, existing_end = code_blocks[block_hash]
                        duplicates.append({
                            "file1": existing_file,
                            "start_line1": existing_start,
                            "end_line1": existing_end,
                            "file2": filepath,
                            "start_line2": i + 1,
                            "end_line2": i + min_lines
                        })
                    else:
                        code_blocks[block_hash] = (filepath, i + 1, i + min_lines)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None, unreadable

    return duplicates, unreadable


def write_report(duplicates, report_file, unreadable=None):
    """
    Writes the duplication report to the specified file.
    """
    unreadable = unreadable or []
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            if not duplicates and not unreadable:
                f.write("No duplicate code blocks found.\n")
                return True

            f.write("Code Duplication Report:\n\n")
            if not duplicates:
                f.write("No duplicate code blocks were found in the files that could be read.\n\n")
            for duplicate in duplicates:
                f.write(f"Duplicate found between:\n")
                f.write(f"  File: {duplicate['file1']}, Lines: {duplicate['start_line1']}-{duplicate['end_line1']}\n")
                f.write(f"  File: {duplicate['file2']}, Lines: {duplicate['start_line2']}-{duplicate['end_line2']}\n")
                f.write("\n")
            if unreadable:
                f.write("Files that could not be read:\n")
                for filepath in unreadable:
                    f.write(f"  File: {filepath}\n")
                f.write("\n")

        logging.info(f"Report written to: {report_file}")
        return True
    except Exception as e:
        logging.error(f"Error writing report to file: {e}")
        return False


def main():
    """
    Main function to run the code duplication detection.
    """
    args = setup_argparse()

    # Input validation
    if not os.path.exists(args.path):
        logging.error(f"Error: Path '{args.path}' does not exist.")
        sys.exit(1)

    if args.min_lines <= 0:
        logging.error("Error: Minimum lines must be a positive integer.")
        sys.exit(1)

    try:
        duplicates, unreadable = find_duplicates(args.path, args.min_lines, args.exclude)
        if duplicates is None:
            logging.error("Failed to find duplicates due to an error.")
            sys.exit(1)

        if not write_report(duplicates, args.report_file, unreadable):
            sys.exit(1)

        if unreadable:
            logging.error(f"Files that could not be read: {', '.join(unreadable)}")
            sys.exit(1)

    except Exception as e:
        logging.error(f"An error occurred during execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    """
    Example Usage:
    python main.py ./my_codebase -m 10 -r my_report.txt -e tests utils
    """
    main()