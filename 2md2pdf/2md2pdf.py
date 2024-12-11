"""
# Description

`tomdtopdf` (pronounced "2 MD 2 PDF") reads from a text file containing markdown content and YAML header metadata, and creates a PDF. It program parses the metadata and markdown content, applies a HTML template, and generates a PDF file with native pagination and a linked table of contents.

In this stage of development the program is designed to be run on individual files from the command line, and exits on the first sign of trouble.

The docstrings and included files can generate documentation with mkdocs. Run `mkdocs build` followed by `mkdocs serve` in the project directory with the dependencies installed.

# Usage

`python project.py <template file> <markdown file>`

# Target Markdown File Requirements

- Must be a text file with the extension '.md'
- Must contain metadata fields in YAML format at the beginning of the file, separated by '---'
- Must contain the following fields:
    - `title`
    - `version`
    - `date_modified`
    - `pdf_filename`

# Included Files

- `docs/index.md`: Markdown template file for mkdocs.
- `input.md`: Example input file.
- `mkdocs.yml`: Configuration file for mkdocs.
- `project.py`: This project's script.
- `README.MD`: The course-specified readme.
- `requirements.txt`: List of dependencies.
- `template.html`: HTML and CSS template file for the Jinja2 module.
- `test_project.py`: Test file for the project.

# Dependencies

- `python-frontmatter`
- `markdown`
- `jinja2`
- `weasyprint`
- `mkdocs`
- `mkdocstrings`
- `mkdocstrings-python`

# Author

Bradley Fidler

# License

MIT License
"""

import sys
import os
from argparse import ArgumentParser
from frontmatter import load
from markdown import Markdown
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS


def arguments():
    """
    Parses command-line arguments with argparse to get the
    template and input file locations.

    :raises SystemExit: if no arguments are provided.
    :return: Namespace object with the template and markdown locations.
    :rtype: argparse.Namespace
    """
    parser = ArgumentParser(description="Convert md to pdf.")
    parser.add_argument(
        "template_location", type=str, help="Location of the template file."
        )
    parser.add_argument(
        "md_location", type=str, help="Location of the markdown file."
        )
    args = parser.parse_args()
    return args


def load_doc(args):
    """
    Load and parse the file contents and metadata with the Frontmatter module.

    :param args: Namespace object with the location of the md file.
    :return: Tuple of metadata and content.
    :rtype: Tuple[Dict[str, str], str]
    """
    try:
        with open(args.md_location, "r", encoding="utf-8") as openfile:
            post = load(openfile)
        metadata, content = post.metadata, post.content
    except Exception as e:
        print(f"load_doc() failed to load or parse input doc: {e}.")
        sys.exit(1)
    return metadata, content


def field_check(metadata):
    """
    Checks for required metadata fields and quits if any are missing.

    :param metadata: Dictionary of metadata fields.
    :raises SystemExit: if any required fields are missing.
    """
    required_fields = ["title", "version", "date_modified", "pdf_filename"]
    for field in required_fields:
        if field not in metadata or not metadata[field]:
            print(f"Metadata field '{field}' is missing or empty.")
            sys.exit(1)


def content_check(content):
    """
    Checks for markdown content in the markdown file and quits if it is missing.

    :param content: String of markdown content.
    :raises SystemExit: if the content is missing.
    """
    if not content:
        print("Markdown content not present.")
        sys.exit(1)
    if not any(line.strip().startswith("#") for line in content.split("\n")):
        print("Suspiciously, the Markdown content does not contain a title; exiting.")
        sys.exit(1)


def md2html(metadata, content, template_location):
    """
    Convert MD to HTML with the Markdown and Jinja2 modules.

    :param metadata: Dictionary of metadata fields.
    :param content: String of markdown content.
    :return: HTML content.
    :rtype: str
    """
    try:
        # Markdown module, convert to html
        md = Markdown(extensions=["toc", "tables"])
        html_content = md.convert(content)  # generate html content
        toc_html = md.toc  # generate html-linked toc

        # Jinja2 module, render html
        template_dir, template_file = os.path.split(template_location)
        template_dir = template_dir if template_dir else "."
        env = Environment(loader=FileSystemLoader(template_dir))  # env object
        template = env.get_template(template_file)  # env load template
        # unpack dictionary of metadata values and add the others
        context = {**metadata, "content": html_content, "toc": toc_html}
        html = template.render(context)  # render the html
        return html

    except Exception as e:
        print(f"md2html() failed to convert md to html: {e}.")
        sys.exit(1)


def html2pdf(metadata, html):
    """
    Render and write the PDF with the Weasyprint module.

    :param metadata: Dictionary of metadata fields. Must include 'pdf_filename' key.
    :param html: String of HTML content to be converted to PDF.
    :raises ValueError: If 'pdf_filename' is not provided in metadata.
    :raises Exception: For any other exceptions that occur during PDF generation.
    """
    try:
        if not metadata.get("pdf_filename"):
            raise ValueError("Cannot access file from pdf_filename.")
        HTML(string=html, base_url='.').write_pdf(metadata["pdf_filename"])
    except Exception as e:
        print(f"html2pdf() failed to generate PDF: {e}.")
        sys.exit(1)


def main():
    """
    Orchestrates the workflow.
    """
    args = arguments()  # get arguments
    metadata, content = load_doc(args)  # extract metadata + content
    field_check(metadata)  # field check
    content_check(content)  # content check
    html = md2html(metadata, content, args.template_location)  # render HTML
    html2pdf(metadata, html)  # render PDF


if __name__ == "__main__":
    main()