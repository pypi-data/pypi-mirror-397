import argparse
import logging
import os
import sys

from rich.logging import RichHandler

from .converter import create_pdf_from_folder


def main():
    # Configure logging
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    log = logging.getLogger("kmakepdf")

    parser = argparse.ArgumentParser(
        description="Convert images and PDFs in a folder to a single PDF."
    )
    parser.add_argument("folder", help="Input folder containing images or PDFs.")
    parser.add_argument(
        "-o",
        "--output",
        help="Output PDF file path. Defaults to <folder>.pdf. Ignored if -r is used.",
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Process subfolders recursively."
    )

    args = parser.parse_args()

    folder = args.folder
    if not os.path.isdir(folder):
        log.error(f"[bold red]Error:[/] {folder} is not a directory.")
        sys.exit(1)

    if args.recursive:
        # Process subfolders
        for subfolder in os.listdir(folder):
            subfolder_path = os.path.join(folder, subfolder)
            if os.path.isdir(subfolder_path):
                output_pdf = os.path.join(folder, f"{subfolder}.pdf")
                log.info(
                    f"Processing [bold cyan]{subfolder}[/] -> [bold green]{output_pdf}[/]"
                )
                create_pdf_from_folder(subfolder_path, output_pdf)
    else:
        # Process single folder
        output_pdf = args.output
        if not output_pdf:
            # Use folder name for output
            output_pdf = f"{folder.rstrip(os.sep)}.pdf"

        log.info(f"Processing [bold cyan]{folder}[/] -> [bold green]{output_pdf}[/]")
        create_pdf_from_folder(folder, output_pdf)


if __name__ == "__main__":
    main()
