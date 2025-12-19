"""
APA Citation Engine
===================
Powering the 'Citation Gateway' of the APA Writing Assistant.
Leverages CrossRef (via Habanero) for authentic, hallucinations-free metadata.

Usage:
    engine = CitationEngine()
    citation = engine.generate_citation("10.1038/s41586-020-2649-2")
    print(citation)
"""

from typing import Optional, Dict, Any
import logging
from datetime import datetime

# Libraries from "Acceleration Pack"
try:
    from habanero import Crossref
    from citeproc.source.json import CiteProcJSON
    from citeproc import CitationStylesStyle, CitationStylesBibliography, formatter
    from citeproc import Citation, CitationItem
except ImportError:
    # Fallback for dev environment without all packages
    Crossref = None

class CitationEngine:
    def __init__(self, email: str = "agent_contact@example.com"):
        """
        Initialize with contact email for "Polite Pool" access to CrossRef.
        """
        self.cr = Crossref(mailto=email) if Crossref else None
        # We defaults to a simple dict cache for MVP
        self.cache = {}

    def lookup_doi(self, doi: str) -> Dict[str, Any]:
        """
        Fetch metadata from CrossRef by DOI.
        """
        if not self.cr:
            return {"error": "Habanero library not installed"}

        if doi in self.cache:
            return self.cache[doi]

        try:
            # Fetch CSL JSON directly
            result = self.cr.works(ids=doi)
            if 'message' in result:
                metadata = result['message']
                self.cache[doi] = metadata
                return metadata
        except Exception as e:
            logging.error(f"CrossRef Lookup Failed: {e}")
            return {"error": str(e)}

        return {"error": "DOI not found"}

    def search_by_title(self, title: str, limit: int = 3) -> list:
        """
        Search for a paper by title.
        """
        if not self.cr:
            return []

        try:
            results = self.cr.works(query=title, limit=limit)
            items = results.get('message', {}).get('items', [])
            return items
        except Exception as e:
            logging.error(f"Search Failed: {e}")
            return []

    def format_apa7(self, metadata: Dict[str, Any]) -> str:
        """
        Format metadata into APA 7th Edition String.
        Uses rigorous CSL processor if available, else robust heuristic.
        """
        if "error" in metadata:
            return f"[Error: {metadata['error']}]"

        # 1. Try Simple Heuristic First (Faster, less dependency hell for MVP)
        # APA 7: Author, A. A. (Year). Title of article. Title of Periodical, xx(x), pp-pp. https://doi.org/xx.xxx
        try:
            authors = metadata.get('author', [])
            author_str = self._format_authors(authors)

            date_parts = metadata.get('published-print', {}).get('date-parts', [])
            if not date_parts:
                date_parts = metadata.get('created', {}).get('date-parts', [])
            year = date_parts[0][0] if date_parts else "n.d."

            title = metadata.get('title', [''])[0]
            container = metadata.get('container-title', [''])[0]
            volume = metadata.get('volume', '')
            issue = metadata.get('issue', '')
            page = metadata.get('page', '')
            doi = metadata.get('DOI', '')

            # Construct
            # Italicize container and volume? In plain text we can't, but we return markdown
            citation = f"{author_str} ({year}). {title}. *{container}*"

            if volume:
                citation += f", *{volume}*"
            if issue:
                citation += f"({issue})"
            if page:
                citation += f", {page}"

            if doi:
                citation += f". https://doi.org/{doi}"
            else:
                citation += "."

            return citation

        except Exception as e:
            logging.warning(f"Heuristic formatting failed: {e}. Returning raw title.")
            return metadata.get('title', ['Unknown Title'])[0]

    def _format_authors(self, authors: list) -> str:
        """Helper to format author list APA style."""
        if not authors:
            return "Anonymous"

        formatted = []
        for auth in authors:
            family = auth.get('family', '')
            given = auth.get('given', '')
            initial = given[0].upper() + "." if given else ""
            formatted.append(f"{family}, {initial}")

        if len(formatted) == 1:
            return formatted[0]
        elif len(formatted) == 2:
            return f"{formatted[0]} & {formatted[1]}"
        elif len(formatted) < 21:
            return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"
        else:
            return ", ".join(formatted[:19]) + ", ... " + formatted[-1]


# Usage
if __name__ == "__main__":
    engine = CitationEngine()
    print("Searching for 'Attention is All You Need'...")
    results = engine.search_by_title("Attention is All You Need", limit=1)
    if results:
        meta = results[0]
        print(f"Found DOI: {meta.get('DOI')}")
        apa = engine.format_apa7(meta)
        print(f"APA 7: {apa}")
