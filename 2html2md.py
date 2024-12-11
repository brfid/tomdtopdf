import os
import re
import sys
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def clean_google_url(url):
    match = re.search(r'q=(https?://[^&]+)', url)
    return match.group(1) if match else url

def remove_line_breaks_within_paragraphs(soup):
    for p in soup.find_all('p'):
        for text_node in p.find_all(string=True):
            new_text = text_node.replace('\n', ' ').replace('\r', ' ')
            text_node.replace_with(new_text)

def increase_heading_levels(markdown_content):
    def replace_heading(match):
        heading = match.group(1)
        return '#' + heading

    return re.sub(r'^(#{1,6})', replace_heading, markdown_content, flags=re.MULTILINE)

def ensure_space_before_links(markdown_content):
    return re.sub(r'(?<!\!)\b(\S)(\[)', r'\1 \2', markdown_content)

def convert_html_to_md(html_content, output_md_file):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Process images
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            img['src'] = os.path.join('images', os.path.basename(src))

    # Process links
    for a in soup.find_all('a', href=True):
        a['href'] = clean_google_url(a['href'])

    # Remove line breaks within paragraphs
    remove_line_breaks_within_paragraphs(soup)

    # Convert to markdown with hash style headings
    markdown_content = md(str(soup), heading_style="ATX")

    # Increase heading levels
    markdown_content = increase_heading_levels(markdown_content)

    # Ensure space before links
    markdown_content = ensure_space_before_links(markdown_content)

    # Write to output file
    with open(output_md_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 2html2md.py <path_to_html_file>")
        sys.exit(1)

    input_html_file = sys.argv[1]
    output_md_file = os.path.splitext(input_html_file)[0] + '.md'

    with open(input_html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    convert_html_to_md(html_content, output_md_file)
    print(f"Markdown file created at: {output_md_file}")