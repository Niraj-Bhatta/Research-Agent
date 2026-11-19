"""IEEE-formatted PDF export using xhtml2pdf.

Styling follows IEEE conference paper conventions:
  - Times Roman serif font throughout
  - 10 pt body text, 24 pt title
  - All text in black (#000000)
  - A4 page with standard IEEE margins
  - Justified body text
"""

import markdown
from xhtml2pdf import pisa

# IEEE-compliant stylesheet
IEEE_CSS = """
@page {
    size: a4;
    margin-top: 0.75in;
    margin-bottom: 1.0in;
    margin-left: 0.625in;
    margin-right: 0.625in;
}
body {
    font-family: 'Times-Roman', Times, serif;
    font-size: 10pt;
    color: #000000;
    line-height: 1.3;
}
/* Title */
h1 {
    font-family: 'Times-Roman', Times, serif;
    font-size: 24pt;
    font-weight: bold;
    text-align: center;
    color: #000000;
    margin-top: 0;
    margin-bottom: 16pt;
}
/* Major sections: II. INTRODUCTION etc. */
h2 {
    font-family: 'Times-Roman', Times, serif;
    font-size: 10pt;
    font-weight: bold;
    text-align: center;
    text-transform: uppercase;
    color: #000000;
    margin-top: 14pt;
    margin-bottom: 6pt;
}
/* Sub-sections */
h3 {
    font-family: 'Times-Roman', Times, serif;
    font-size: 10pt;
    font-weight: bold;
    font-style: italic;
    color: #000000;
    margin-top: 10pt;
    margin-bottom: 4pt;
}
h4 {
    font-family: 'Times-Roman', Times, serif;
    font-size: 10pt;
    font-style: italic;
    color: #000000;
    margin-top: 8pt;
    margin-bottom: 4pt;
}
p {
    font-family: 'Times-Roman', Times, serif;
    font-size: 10pt;
    color: #000000;
    text-align: justify;
    text-indent: 0.25in;
    margin-top: 0;
    margin-bottom: 6pt;
}
ul, ol {
    font-family: 'Times-Roman', Times, serif;
    font-size: 10pt;
    color: #000000;
    margin-left: 0.4in;
    margin-bottom: 6pt;
}
li {
    margin-bottom: 2pt;
}
a {
    color: #000000;
    text-decoration: none;
}
table {
    border-collapse: collapse;
    font-size: 9pt;
    margin-top: 6pt;
    margin-bottom: 6pt;
}
th, td {
    border: 1px solid #000;
    padding: 3pt 6pt;
    color: #000000;
}
th {
    font-weight: bold;
    text-align: center;
    background-color: #f0f0f0;
}
blockquote {
    font-size: 9pt;
    font-style: italic;
    color: #000000;
    margin-left: 0.4in;
    margin-right: 0.4in;
}
"""


def markdown_to_pdf(md_text: str, pdf_path: str) -> None:
    """Convert Markdown to an IEEE-formatted PDF."""
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code"],
    )
    document = (
        "<!DOCTYPE html>"
        "<html><head><meta charset='utf-8'>"
        f"<style>{IEEE_CSS}</style>"
        f"</head><body>{html_body}</body></html>"
    )
    with open(pdf_path, "wb") as fh:
        result = pisa.CreatePDF(document, dest=fh)
    if result.err:
        raise RuntimeError(f"PDF generation failed (xhtml2pdf error count: {result.err})")
