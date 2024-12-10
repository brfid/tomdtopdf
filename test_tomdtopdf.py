import pytest
from project import arguments, load_doc, field_check, content_check, md2html
from argparse import Namespace
from datetime import date


@pytest.fixture
def test_md_file(tmp_path):
    """
    Create a test markdown input file.
    """
    test_md_content = (
        "---\n"
        "title: Test Title\n"
        "version: 1.0\n"
        "date_modified: 2024-12-04\n"
        "pdf_filename: test.pdf\n"
        "---\n"
        "# Test Content"
    )
    md_file = tmp_path / "test.md"
    md_file.write_text(test_md_content)
    return md_file


@pytest.fixture
def test_html_file(tmp_path):
    """
    Use a fixture to create a test HTML template file.
    """
    test_html_content = (
        "<html>\n"
        "<head><title>Test Title</title></head>\n"
        "<body>Test Content</body>\n"
        "</html>"
    )
    test_html_file = tmp_path / "test_template.html"
    test_html_file.write_text(test_html_content)
    return test_html_file


def test_arguments(monkeypatch):
    """
    Test arguments() function to parse command-line arguments.
    """
    test_args = ["project.py", "template.html", "input.md"]  # fake
    monkeypatch.setattr("sys.argv", test_args)  # monkey tricks
    args = arguments()
    assert args.template_location == "template.html"
    assert args.md_location == "input.md"


def test_load_doc(test_md_file):
    """
    Test load_doc() function and that `date_modified` and `version`
    are transformed types.
    Test load_doc() will exit if it fails to load the input doc.
    """
    args = Namespace(md_location=str(test_md_file))
    metadata, content = load_doc(args)
    assert metadata["title"] == "Test Title"
    assert metadata["version"] == 1.0
    assert metadata["date_modified"] == date(2024, 12, 4)
    assert metadata["pdf_filename"] == "test.pdf"
    assert content == "# Test Content"

    # Test load_doc() with non-existent input file
    args = Namespace(location="non_existent.md")
    with pytest.raises(SystemExit):
        load_doc(args)


def test_field_check():
    """
    Test field_check() function with all required fields present.
    Test that field_check() will exit if any required fields are missing.
    """
    metadata = {
        "title": "Test Title",
        "version": "1.0",
        "date_modified": "2024-12-04",
        "pdf_filename": "test.pdf",
    }
    field_check(metadata)

    # Test field_check() with missing required fields
    metadata.pop("title")
    with pytest.raises(SystemExit):
        field_check(metadata)


def test_content_check(test_md_file):
    """
    Test content_check() function with content present and missing title.
    Test that content_check() will exit if the content is missing.
    """
    args = Namespace(md_location=str(test_md_file))
    _, content = load_doc(args)

    # Test content_check() with valid content
    content_check(content)

    # Test content_check() with missing content
    with pytest.raises(SystemExit):
        content_check("")

    # Test content_check() with content missing a title
    with pytest.raises(SystemExit):
        content_check("Hello, World!")


def test_md2html(test_md_file):
    """
    Test md2html() function with valid metadata and content.
    Test that md2html() will exit if the template file is missing.
    """
    args = Namespace(md_location=str(test_md_file), template_location="template.html")
    metadata, content = load_doc(args)
    html_content = md2html(metadata, content, args.template_location)
    assert "Test Content" in html_content

    # Test md2html() with non-existent template file
    with pytest.raises(SystemExit):
        md2html(metadata, content, "non_existent.html")
