"""TOON export utility for Docling documents."""

import logging
from pathlib import Path
from typing import Union

try:
    import toon
except ImportError:
    toon = None  # type: ignore

from docling_core.types.doc import DoclingDocument

_log = logging.getLogger(__name__)


def save_as_toon(
    doc: DoclingDocument,
    filename: Union[str, Path],
) -> None:
    """
    Save a DoclingDocument as TOON format.

    TOON (Token-Oriented Object Notation) is a compact, human-readable
    serialization format designed to reduce token usage when passing
    structured data to Large Language Models (LLMs).

    Args:
        doc: The DoclingDocument to export
        filename: Path where the TOON file should be saved

    Raises:
        ImportError: If the toon library is not installed
        IOError: If the file cannot be written
    """
    if toon is None:
        raise ImportError(
            "The 'toon' library is required for TOON export. "
            "Install it with: pip install toon"
        )

    _log.info(f"Exporting document to TOON format: {filename}")

    # Convert DoclingDocument to a dictionary that can be serialized
    # Use the model_dump method from Pydantic to get a dict representation
    doc_dict = doc.model_dump(
        mode="json",
        exclude_none=True,
        by_alias=True,
    )

    # Serialize to TOON format
    toon_content = toon.encode(doc_dict)

    # Write to file
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(toon_content)

    _log.info(f"Successfully wrote TOON output to {filename}")
