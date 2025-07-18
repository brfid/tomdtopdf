#!/usr/bin/env python3
"""
tomdtopdf.py

Read and parses YAML Frontmatter markdown files, applies a HTML+CSS template,
and generates a PDF file with native pagination and a linked table of contents.

`python project.py <template file> <markdown file>`

Source files must be in 'YAML Frontmatter' format: a markdown file (`.md`)
with a YAML header (separated by `---`).

The YAML header must contain a mapping with the following key-value pairs:
`title`, `version`, `date_modified`, `pdf_filename`.

Included files:

- `input.md`: Example input file.
- `tomdtopdf`: This project's script.
- `README.MD`: The course-specified readme.
- `requirements.txt`: List of dependencies.
- `template.html`: HTML and CSS template file for the Jinja2 module.
"""

import sys
import os
from argparse import ArgumentParser
from frontmatter import load
from markdown import Markdown
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


def arguments():
    """
    Parses command-line arguments with argparse to get the
    template and input file locations.
    """
    parser = ArgumentParser(description="Convert md to pdf.")
    parser.add_argument(
        "template_location", type=str, help="Location of the template file."
    )
    parser.add_argument("md_location", type=str, help="Md file location.")
    args = parser.parse_args()
    return args


def load_doc(args):
    """
    Load and parse the file contents and metadata with the Frontmatter module.
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
    """
    required_fields = ["title", "version", "date_modified", "pdf_filename"]
    for field in required_fields:
        if field not in metadata or not metadata[field]:
            print(f"Metadata field '{field}' is missing or empty.")
            sys.exit(1)


def content_check(content):
    """
    Checks for markdown content in the markdown file and quits if it is missing.
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
    """
    try:
        # Convert Markdown to HTML
        md = Markdown(extensions=["toc", "tables"])
        html_content = md.convert(content)
        toc_html = md.toc

        # Set up Jinja2 environment
        template_dir, template_file = os.path.split(template_location)
        template_dir = template_dir if template_dir else "."
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_file)

        # Render HTML with context
        context = {**metadata, "content": html_content, "toc": toc_html}
        html = template.render(context)

        # Return HTML content and template directory
        return html, template_dir

    except Exception as e:
        print(f"md2html() failed to convert md to html: {e}.")
        sys.exit(1)


def html2pdf(metadata, html):
    """
    Render and write the PDF with the Weasyprint module.
    """
    try:
        if not metadata.get("pdf_filename"):
            raise ValueError("Cannot access file from pdf_filename.")
        # Updated base_url to properly resolve image paths
        HTML(string=html, base_url=os.getcwd()).write_pdf(metadata["pdf_filename"])
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
    html, template_dir = md2html(
        metadata, content, args.template_location
    )  # render HTML
    html2pdf(metadata, html)  # render PDF


if __name__ == "__main__":
    main()
