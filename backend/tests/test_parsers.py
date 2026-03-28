from __future__ import annotations

import base64
from io import BytesIO
import unittest
from zipfile import ZipFile

from app.schemas.citation import DocumentFormat, SourceAsset
from app.services.parsers.bibtex import parse_bibtex_entries
from app.services.parsers.docx import extract_docx_text, parse_docx_citations
from app.services.parsers.latex import parse_latex_citations, parse_latex_sections
from app.services.parsers.pdf import parse_pdf_citations


class ParserTests(unittest.TestCase):
    def test_parse_bibtex_entries(self) -> None:
        text = """
        @article{vaswani2017attention,
          title={Attention Is All You Need},
          author={Vaswani, Ashish and Shazeer, Noam},
          year={2017},
          journal={NeurIPS},
          doi={10.48550/arXiv.1706.03762}
        }
        """
        entries = parse_bibtex_entries(text)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].reference_id, "vaswani2017attention")
        self.assertEqual(entries[0].year, 2017)

    def test_parse_latex_citations_and_sections(self) -> None:
        text = r"""
        \section{Methods}
        We build on the Transformer backbone \cite{vaswani2017attention}.
        """
        citations = parse_latex_citations(text)
        sections = parse_latex_sections(text)
        self.assertEqual(sections, ["Methods"])
        self.assertEqual(citations[0].reference_keys, ["vaswani2017attention"])

    def test_parse_docx_text_and_citations(self) -> None:
        buffer = BytesIO()
        with ZipFile(buffer, "w") as archive:
            archive.writestr(
                "word/document.xml",
                """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
                  <w:body>
                    <w:p><w:r><w:t>Prior work [Smith 2020] remains strong.</w:t></w:r></w:p>
                  </w:body>
                </w:document>
                """,
            )
        text = extract_docx_text(buffer.getvalue())
        citations = parse_docx_citations(text)
        self.assertIn("Smith 2020", citations[0].reference_keys[0])

    def test_parse_pdf_citations_without_pdf_dependency(self) -> None:
        text = "Our approach improves on prior work [1, 2] and (Smith 2020)."
        citations = parse_pdf_citations(text)
        self.assertEqual(len(citations), 2)


if __name__ == "__main__":
    unittest.main()
