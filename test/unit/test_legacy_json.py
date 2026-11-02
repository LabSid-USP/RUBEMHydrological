"""Export of a plugin INI project to RUBEM legacy JSON."""

from __future__ import annotations

import configparser
import json
import logging
from pathlib import Path

import pytest

from plugin.validation.legacy_json import legacy_json_document, write_legacy_json
from plugin.validation.schemas import defaultConfigSchema


def _project() -> configparser.ConfigParser:
    """Return the default project the dialog seeds."""
    parser = configparser.ConfigParser()
    parser.read_dict(defaultConfigSchema)
    return parser


@pytest.mark.unit
def test_default_project_exports_numbers_and_omits_plugin_keys() -> None:
    """The live defaults become legacy JSON without a version field."""
    document, diagnostics = legacy_json_document(_project())

    assert "version" not in document
    assert document["CALIBRATION"]["alpha"] == 4.5
    assert document["GRID"]["grid"] == 500.0
    assert document["GENERATE_FILE"]["itp"] is True
    assert document["GENERATE_FILE"]["arn"] is False
    assert document["SIM_TIME"]["start"] == "01/01/1900"
    assert "input" not in document["DIRECTORIES"]
    assert "demtif" not in document["RASTERS"]
    assert "georeference" not in document["RASTERS"]
    assert any("DIRECTORIES.input" in note for note in diagnostics)


@pytest.mark.unit
def test_demtif_is_renamed_and_comma_decimal_writes_nothing(tmp_path: Path) -> None:
    """``demtif`` becomes ``georeference``. A comma decimal leaves no file."""
    parser = _project()
    parser.set("RASTERS", "demtif", "dem/dem.tif")
    document, _diagnostics = legacy_json_document(parser)
    assert document["RASTERS"]["georeference"] == "dem/dem.tif"

    parser.set("CALIBRATION", "alpha", "4,5")
    destination = tmp_path / "basin.rubem.json"
    with pytest.raises(ValueError, match="decimal separator"):
        write_legacy_json(parser, destination)
    assert not destination.exists()


@pytest.mark.unit
def test_ini_round_trip_keeps_alpha_and_unknown_project_key(tmp_path: Path) -> None:
    """The project INI keeps values the exporter does not own."""
    parser = _project()
    parser.set("CALIBRATION", "alpha", "4.500")
    parser.set("CALIBRATION", "notes", "keep me")
    project = tmp_path / "basin.ini"
    with project.open("w", encoding="utf-8") as handle:
        parser.write(handle)

    loaded = configparser.ConfigParser()
    loaded.read(project, encoding="utf-8")
    assert loaded.get("CALIBRATION", "alpha", raw=True) == "4.500"
    assert loaded.get("CALIBRATION", "notes", raw=True) == "keep me"

    document, diagnostics = legacy_json_document(loaded)
    assert document["CALIBRATION"]["alpha"] == 4.5
    assert "notes" not in document["CALIBRATION"]
    assert any("CALIBRATION.notes" in note for note in diagnostics)


@pytest.mark.unit
def test_missing_arn_defaults_to_false() -> None:
    """An INI saved before ``arn`` existed still exports."""
    parser = _project()
    parser.remove_option("GENERATE_FILE", "arn")
    document, _diagnostics = legacy_json_document(parser)
    assert document["GENERATE_FILE"]["arn"] is False


@pytest.mark.unit
def test_iso_date_is_rejected() -> None:
    """Legacy JSON keeps DD/MM/YYYY and refuses an ISO date."""
    parser = _project()
    parser.set("SIM_TIME", "start", "1900-01-01")
    with pytest.raises(ValueError, match="DD/MM/YYYY"):
        legacy_json_document(parser)


@pytest.mark.unit
def test_pinned_schema_accepts_the_document_when_pydantic_is_present() -> None:
    """The pinned RUBEM model validates the document when pydantic is installed."""
    pytest.importorskip("pydantic")
    root = Path(__file__).resolve().parents[2]
    model_root = root / "external" / "rubem-model"
    if not (
        model_root / "rubem" / "configuration" / "model_configuration_file.py"
    ).is_file():
        pytest.skip("RUBEM submodule is not initialized")

    import sys

    sys.path.insert(0, str(model_root))
    from rubem.configuration.model_configuration_file import ModelConfigurationFile

    document, _diagnostics = legacy_json_document(_project())
    logger = logging.getLogger("rubem.configuration.model_configuration_file")
    records: list[logging.LogRecord] = []
    handler = logging.Handler()
    handler.emit = records.append  # type: ignore[method-assign]
    logger.addHandler(handler)
    try:
        validated = ModelConfigurationFile.model_validate(document)
    finally:
        logger.removeHandler(handler)
    dumped = validated.model_dump(by_alias=True)
    assert dumped["CALIBRATION"]["alpha"] == 4.5
    assert dumped["GENERATE_FILE"]["arn"] is False
    unknown = [record for record in records if "Unknown key" in record.getMessage()]
    assert unknown == []


@pytest.mark.unit
def test_written_file_is_the_document(tmp_path: Path) -> None:
    """The file on disk matches the in-memory document."""
    destination = tmp_path / "basin.rubem.json"
    document, _diagnostics = legacy_json_document(_project())
    write_legacy_json(_project(), destination)
    assert json.loads(destination.read_text(encoding="utf-8")) == document
