import logging
import os
from pypdf import PdfWriter, PdfReader
from PIL import Image


log = logging.getLogger("kmakepdf")


def create_pdf_from_folder(folder_path: str, output_pdf: str) -> None:
    pdf_writer = PdfWriter()

    files = sorted(os.listdir(folder_path))
    count = 0

    for file_name in files:
        file_path = os.path.join(folder_path, file_name)

        if file_name.lower().endswith(".pdf"):
            log.info(f"Adding PDF: [cyan]{file_name}[/]")
            try:
                with open(file_path, "rb") as f:
                    pdf_reader = PdfReader(f)
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)
                count += 1
            except Exception as e:
                log.error(f"[bold red]Error reading PDF {file_name}:[/] {e}")

        elif file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            log.info(f"Converting Image: [magenta]{file_name}[/]")
            try:
                image = Image.open(file_path).convert("RGB")
                # Convert image to a single-page PDF in memory
                with open(f"{file_path}.pdf", "wb") as temp_pdf:
                    image.save(temp_pdf, "PDF")
                # Add the single-page PDF we just created
                with open(f"{file_path}.pdf", "rb") as temp_f:
                    pdf_reader = PdfReader(temp_f)
                    pdf_writer.add_page(pdf_reader.pages[0])

                # Clean up temp file
                if os.path.exists(f"{file_path}.pdf"):
                    os.remove(f"{file_path}.pdf")
                count += 1
            except Exception as e:
                log.error(f"[bold red]Error processing image {file_name}:[/] {e}")

    # Write out the combined PDF for the folder
    log.info(f"Writing final PDF to [bold green]{output_pdf}[/] ({count} files merged)")
    try:
        with open(output_pdf, "wb") as out_f:
            pdf_writer.write(out_f)
        log.info("[bold green]Success![/]")
    except Exception as e:
        log.error(f"[bold red]Failed to write output PDF:[/] {e}")
