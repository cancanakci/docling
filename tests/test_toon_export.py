"""Tests for TOON export functionality."""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from typer.testing import CliRunner

from docling.cli.main import app
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

runner = CliRunner()


def test_toon_import():
    """Test that the toon library can be imported."""
    try:
        import toon

        assert toon is not None
    except ImportError:
        pytest.skip("toon library not installed")


def test_toon_export_programmatic(tmp_path):
    """Test TOON export using DocumentConverter API."""
    source = Path("./tests/data/pdf/2305.03393v1-pg9.pdf")
    if not source.exists():
        pytest.skip(f"Test file {source} not found")

    try:
        import toon
    except ImportError:
        pytest.skip("toon library not installed")

    # Set up converter
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = False

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    # Convert document
    result = converter.convert(source)

    # Export to TOON
    from docling.utils.toon_export import save_as_toon

    output_file = tmp_path / "test_output.toon"
    save_as_toon(result.document, output_file)

    # Verify output
    assert output_file.exists(), "TOON output file was not created"
    assert output_file.stat().st_size > 0, "TOON output file is empty"

    # Verify the content can be parsed back
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
        parsed_data = toon.decode(content)
        assert parsed_data is not None, "Failed to parse TOON output"
        assert isinstance(parsed_data, dict), "Parsed TOON data is not a dictionary"


def test_cli_toon_export(tmp_path):
    """Test TOON export via CLI."""
    source = "./tests/data/pdf/2305.03393v1-pg9.pdf"
    if not Path(source).exists():
        pytest.skip(f"Test file {source} not found")

    try:
        import toon  # noqa: F401
    except ImportError:
        pytest.skip("toon library not installed")

    output = tmp_path / "out"
    output.mkdir()

    # Run the CLI with TOON output format
    result = runner.invoke(app, [source, "--to", "toon", "--output", str(output)])

    # Check if the command succeeded
    assert result.exit_code == 0, f"CLI command failed: {result.stdout}"

    # Verify the output file was created
    expected_file = output / f"{Path(source).stem}.toon"
    assert expected_file.exists(), f"TOON output file {expected_file} was not created"
    assert expected_file.stat().st_size > 0, "TOON output file is empty"


def test_cli_toon_export_with_multiple_formats(tmp_path):
    """Test that TOON can be exported alongside other formats."""
    source = "./tests/data/pdf/2305.03393v1-pg9.pdf"
    if not Path(source).exists():
        pytest.skip(f"Test file {source} not found")

    try:
        import toon  # noqa: F401
    except ImportError:
        pytest.skip("toon library not installed")

    output = tmp_path / "out"
    output.mkdir()

    # Export to both JSON and TOON
    result = runner.invoke(
        app, [source, "--to", "json", "--to", "toon", "--output", str(output)]
    )

    assert result.exit_code == 0, f"CLI command failed: {result.stdout}"

    # Verify both files were created
    stem = Path(source).stem
    json_file = output / f"{stem}.json"
    toon_file = output / f"{stem}.toon"

    assert json_file.exists(), "JSON output file was not created"
    assert toon_file.exists(), "TOON output file was not created"
    assert json_file.stat().st_size > 0, "JSON file is empty"
    assert toon_file.stat().st_size > 0, "TOON file is empty"


def test_toon_export_with_tempfile():
    """Test TOON export with temporary files (similar to patent export tests)."""
    source = Path("./tests/data/pdf/2305.03393v1-pg9.pdf")
    if not source.exists():
        pytest.skip(f"Test file {source} not found")

    try:
        import toon  # noqa: F401
    except ImportError:
        pytest.skip("toon library not installed")

    # Convert document
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = False

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    result = converter.convert(source)
    doc = result.document

    # Test export to temporary file
    from docling.utils.toon_export import save_as_toon

    with NamedTemporaryFile(suffix=".toon", delete=False) as tmp_file:
        save_as_toon(doc, Path(tmp_file.name))
        assert os.path.getsize(tmp_file.name) > 0, "TOON file is empty"

