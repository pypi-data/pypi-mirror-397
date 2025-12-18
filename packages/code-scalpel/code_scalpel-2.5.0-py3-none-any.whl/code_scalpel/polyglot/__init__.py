"""
Code Scalpel Polyglot Module - Multi-language code analysis.

[20251214_FEATURE] v2.0.0 - Unified interface for Python, JavaScript, TypeScript, and Java.

This module provides:
- PolyglotExtractor: Multi-language code extraction
- Language detection from file extensions
- Unified IR-based analysis
"""

from code_scalpel.polyglot.extractor import (
    Language,
    PolyglotExtractor,
    PolyglotExtractionResult,
    detect_language,
    extract_from_file,
    extract_from_code,
    EXTENSION_MAP,
)

__all__ = [
    "Language",
    "PolyglotExtractor",
    "PolyglotExtractionResult",
    "detect_language",
    "extract_from_file",
    "extract_from_code",
    "EXTENSION_MAP",
]
