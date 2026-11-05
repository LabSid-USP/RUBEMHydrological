"""Export of a plugin INI project to RUBEM legacy JSON."""

from __future__ import annotations

import configparser
import json
import logging
import os
from pathlib import Path

import pytest

from plugin.validation.legacy_json import (
    legacy_json_document,
    read_legacy_json,
    write_legacy_json,
)
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
    with pytest.raises(ValueError, match="CALIBRATION.alpha"):
        write_legacy_json(parser, destination)
    assert not destination.exists()


@pytest.mark.unit
def test_json_project_round_trip_keeps_alpha_and_demtif(tmp_path: Path) -> None:
    """The file on disk is legacy JSON, and the dialog parser can read it back."""
    parser = _project()
    parser.set("CALIBRATION", "alpha", "4.500")
    parser.set("RASTERS", "demtif", "dem/dem.tif")
    project = tmp_path / "basin.json"
    write_legacy_json(parser, project)
    loaded = read_legacy_json(project)
    assert loaded.getfloat("CALIBRATION", "alpha") == 4.5
    assert loaded.get("RASTERS", "demtif") == "dem/dem.tif"
    on_disk = json.loads(project.read_text(encoding="utf-8"))
    assert on_disk["RASTERS"]["georeference"] == "dem/dem.tif"
    assert "version" not in on_disk


@pytest.mark.unit
def test_format_1_0_is_rejected() -> None:
    """A versioned RUBEM document is not edited as if it were the legacy shape."""
    from plugin.validation.legacy_json import config_from_legacy_document

    with pytest.raises(ValueError, match="version"):
        config_from_legacy_document(
            {
                "version": "1.0",
                "SIM_TIME": {"start": "01/01/1900", "end": "01/02/1900"},
            }
        )


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
    with pytest.raises(ValueError, match="%d/%m/%Y"):
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
def test_float_text_keeps_more_than_three_decimals() -> None:
    """Loading a project must not round scientific values to three places."""
    from plugin.validation.legacy_json import _as_ini_text

    parser = _project()
    parser.set("CALIBRATION", "w_1", "0.3333333333")
    parser.set("CALIBRATION", "w_2", "0.3333333333")
    parser.set("CALIBRATION", "w_3", "0.3333333334")
    document, _diagnostics = legacy_json_document(parser)
    text = _as_ini_text(document["CALIBRATION"]["w_1"])
    assert text.startswith("0.3333333333")
    assert _as_ini_text(-0.0001) == "-0.0001"


@pytest.mark.unit
def test_relative_directory_is_kept_as_written(tmp_path: Path) -> None:
    """The dialog parser stores relative paths exactly as the JSON file has them."""
    parser = _project()
    parser.set("DIRECTORIES", "prec", "data/prec")
    parser.set("FILENAME_PREFIXES", "prec_prefix", "pr")
    project = tmp_path / "basin.json"
    write_legacy_json(parser, project)
    loaded = read_legacy_json(project)
    assert loaded.get("DIRECTORIES", "prec") == "data/prec"
    assert loaded.get("FILENAME_PREFIXES", "prec_prefix") == "pr"
    assert (
        json.loads(project.read_text(encoding="utf-8"))["DIRECTORIES"]["prec"]
        == "data/prec"
    )


@pytest.mark.unit
def test_directory_widget_does_not_erase_a_stored_prefix() -> None:
    """A line edit that holds only the directory keeps the saved series prefix."""
    from plugin.dialog._project import _apply_series

    parser = _project()
    parser.set("DIRECTORIES", "prec", "data/prec/")
    parser.set("FILENAME_PREFIXES", "prec_prefix", "pr")
    holder = type("Holder", (), {"config": parser})()
    _apply_series(holder, "data/prec/", "prec", "prec_prefix")
    assert holder.config.get("FILENAME_PREFIXES", "prec_prefix") == "pr"


@pytest.mark.unit
def test_relative_directory_without_slash_keeps_series_prefix() -> None:
    """A bare relative directory must not become parent-dir + last-segment prefix."""
    from plugin.dialog._project import _apply_series

    parser = _project()
    parser.set("DIRECTORIES", "prec", "data/prec")
    parser.set("FILENAME_PREFIXES", "prec_prefix", "rain")
    holder = type("Holder", (), {"config": parser, "projectFilePath": ""})()
    _apply_series(holder, "data/prec", "prec", "prec_prefix")
    assert holder.config.get("DIRECTORIES", "prec") == "data/prec"
    assert holder.config.get("FILENAME_PREFIXES", "prec_prefix") == "rain"


@pytest.mark.unit
def test_series_file_path_still_updates_directory_and_prefix() -> None:
    """Selecting a map series file still stores its directory and alphabetic prefix."""
    from plugin.dialog._project import _apply_series

    parser = _project()
    parser.set("DIRECTORIES", "prec", "")
    parser.set("FILENAME_PREFIXES", "prec_prefix", "")
    holder = type("Holder", (), {"config": parser, "projectFilePath": ""})()
    _apply_series(holder, "data/prec/rain00000.001", "prec", "prec_prefix")
    assert holder.config.get("DIRECTORIES", "prec") == "data/prec/"
    assert holder.config.get("FILENAME_PREFIXES", "prec_prefix") == "rain"


@pytest.mark.unit
def test_split_dir_file_prefix_root_file_is_not_double_slash() -> None:
    """Root-like dirs (``/``, ``//``) must become ``./``, never ``///``."""
    from plugin.utils.series import splitDirFilePrefix

    assert splitDirFilePrefix("/rain00000.001") == ("./", "rain")
    assert splitDirFilePrefix("//rain00000.001") == ("./", "rain")
    assert splitDirFilePrefix("rain00000.001") == ("./", "rain")


@pytest.mark.unit
def test_apply_series_keeps_dotted_directory_as_directory() -> None:
    """A non-existent ``data/prec.v2`` must not be split into prefix ``prec``."""
    from plugin.dialog._project import _apply_series

    parser = _project()
    parser.set("DIRECTORIES", "prec", "")
    parser.set("FILENAME_PREFIXES", "prec_prefix", "rain")
    holder = type("Holder", (), {"config": parser, "projectFilePath": ""})()
    _apply_series(holder, "data/prec.v2", "prec", "prec_prefix")
    assert holder.config.get("DIRECTORIES", "prec") == "data/prec.v2"
    assert holder.config.get("FILENAME_PREFIXES", "prec_prefix") == "rain"


@pytest.mark.unit
def test_series_field_text_keeps_relative_directory_portable(tmp_path) -> None:
    """Open+Save must not rewrite a relative series dir to an absolute map path."""
    import configparser

    from plugin.dialog._project import _apply_series, _series_field_text

    series_dir = tmp_path / "data" / "prec"
    series_dir.mkdir(parents=True)
    (series_dir / "rain00000.001").write_text("x", encoding="utf-8")
    parser = configparser.ConfigParser()
    parser.read_dict(
        {
            "DIRECTORIES": {"prec": "data/prec"},
            "FILENAME_PREFIXES": {"prec_prefix": "rain"},
        }
    )
    holder = type(
        "Holder",
        (),
        {
            "config": parser,
            "projectFilePath": str(tmp_path / "basin.json"),
        },
    )()
    shown = _series_field_text(holder, "data/prec", "prec_prefix")
    assert shown == os.path.join("data/prec", "rain00000.001")
    assert not os.path.isabs(shown)
    _apply_series(holder, shown, "prec", "prec_prefix")
    stored_dir = holder.config.get("DIRECTORIES", "prec")
    assert stored_dir in ("data/prec/", "data/prec")
    assert not os.path.isabs(stored_dir)
    assert holder.config.get("FILENAME_PREFIXES", "prec_prefix") == "rain"


@pytest.mark.unit
def test_bare_series_filename_does_not_become_filesystem_root(tmp_path) -> None:
    """A project-relative ``rain00000.001`` must not store DIRECTORIES as ``/``."""
    from plugin.dialog._project import _apply_series
    from plugin.utils.series import splitDirFilePrefix

    assert splitDirFilePrefix("rain00000.001") == ("./", "rain")

    series = tmp_path / "rain00000.001"
    series.write_text("x", encoding="utf-8")
    parser = _project()
    parser.set("DIRECTORIES", "prec", "data/prec/")
    parser.set("FILENAME_PREFIXES", "prec_prefix", "rain")
    holder = type(
        "Holder",
        (),
        {"config": parser, "projectFilePath": str(tmp_path / "basin.json")},
    )()
    _apply_series(holder, "rain00000.001", "prec", "prec_prefix")
    stored_dir = holder.config.get("DIRECTORIES", "prec")
    assert stored_dir != "/"
    assert not os.path.isabs(stored_dir) or stored_dir.startswith(str(tmp_path))
    assert holder.config.get("FILENAME_PREFIXES", "prec_prefix") == "rain"


@pytest.mark.unit
def test_get_first_map_series_accepts_directory_without_trailing_slash(
    tmp_path,
) -> None:
    """``data/landuse`` must search inside the directory, not ``data/landuse*.0*``."""
    from plugin.utils.series import getFirstFileNameMapSeries

    series_dir = tmp_path / "landuse"
    series_dir.mkdir()
    sample = series_dir / "use00000.001"
    sample.write_text("x", encoding="utf-8")
    found = getFirstFileNameMapSeries(str(series_dir))
    assert found == str(sample)


@pytest.mark.unit
def test_get_first_map_series_honors_stored_prefix(tmp_path) -> None:
    """A stored prefix must win over another map that sorts first."""
    from plugin.utils.series import getFirstFileNameMapSeries

    series_dir = tmp_path / "prec"
    series_dir.mkdir()
    (series_dir / "other00000.001").write_text("o", encoding="utf-8")
    rain = series_dir / "rain00000.001"
    rain.write_text("r", encoding="utf-8")
    assert getFirstFileNameMapSeries(str(series_dir), prefix="rain") == str(rain)


@pytest.mark.unit
def test_series_field_text_keeps_directory_when_no_maps(tmp_path) -> None:
    """An empty series directory must not become ``.`` in the line edit."""
    import configparser

    from plugin.dialog._project import _series_field_text

    series_dir = tmp_path / "prec"
    series_dir.mkdir()
    parser = configparser.ConfigParser()
    parser.add_section("FILENAME_PREFIXES")
    parser.set("FILENAME_PREFIXES", "prec_prefix", "rain")
    holder = type(
        "Holder",
        (),
        {
            "config": parser,
            "projectFilePath": str(tmp_path / "basin.json"),
        },
    )()
    assert _series_field_text(holder, "prec", "prec_prefix") == "prec"


@pytest.mark.unit
def test_conflicting_aliases_are_rejected() -> None:
    """The plugin must not pick one of two values the model itself rejects."""
    from plugin.validation.legacy_json import config_from_legacy_document

    document, _diagnostics = legacy_json_document(_project())
    document["CALIBRATION"]["beta"] = 0.9
    with pytest.raises(ValueError, match="Conflicting values"):
        config_from_legacy_document(document)


@pytest.mark.unit
def test_written_file_is_the_document(tmp_path: Path) -> None:
    """The file on disk matches the in-memory document."""
    destination = tmp_path / "basin.rubem.json"
    document, _diagnostics = legacy_json_document(_project())
    write_legacy_json(_project(), destination)
    assert json.loads(destination.read_text(encoding="utf-8")) == document


@pytest.mark.unit
def test_unknown_bool_token_is_rejected() -> None:
    """A boolean token the model cannot read is an error, not a silent false."""
    from plugin.validation.legacy_json import config_from_legacy_document

    document, _diagnostics = legacy_json_document(_project())
    document["GENERATE_FILE"]["arn"] = "maybe"
    with pytest.raises(ValueError, match=r"GENERATE_FILE\.arn"):
        config_from_legacy_document(document)


@pytest.mark.unit
def test_known_bool_tokens_are_accepted_on_load() -> None:
    """Recognized yes/no spellings still load as booleans."""
    from plugin.validation.legacy_json import config_from_legacy_document

    document, _diagnostics = legacy_json_document(_project())
    document["GENERATE_FILE"]["arn"] = "YES"
    document["RASTER_FILE_FORMAT"]["map_raster_series"] = "0"
    loaded = config_from_legacy_document(document)
    assert loaded.getboolean("GENERATE_FILE", "arn") is True
    assert loaded.getboolean("RASTER_FILE_FORMAT", "map_raster_series") is False


@pytest.mark.unit
def test_padded_bool_tokens_are_normalized_on_load() -> None:
    """Whitespace around a known token must not become a silent false."""
    from plugin.validation.legacy_json import config_from_legacy_document

    document, _diagnostics = legacy_json_document(_project())
    document["GENERATE_FILE"]["arn"] = " YES "
    document["RASTER_FILE_FORMAT"]["map_raster_series"] = " false "
    loaded = config_from_legacy_document(document)
    assert loaded.getboolean("GENERATE_FILE", "arn") is True
    assert loaded.getboolean("RASTER_FILE_FORMAT", "map_raster_series") is False


@pytest.mark.unit
def test_missing_arn_defaults_to_false_on_load() -> None:
    """Files written before ``arn`` existed open with arn disabled."""
    from plugin.validation.legacy_json import config_from_legacy_document

    document, _diagnostics = legacy_json_document(_project())
    del document["GENERATE_FILE"]["arn"]
    loaded = config_from_legacy_document(document)
    assert loaded.getboolean("GENERATE_FILE", "arn") is False


@pytest.mark.unit
def test_written_file_honors_umask(tmp_path: Path) -> None:
    """The new JSON file is not forced to 0o600 by tempfile.mkstemp."""
    import os
    import stat

    destination = tmp_path / "basin.json"
    write_legacy_json(_project(), destination)
    mode = stat.S_IMODE(os.stat(destination).st_mode)
    current = os.umask(0)
    os.umask(current)
    assert mode == 0o666 & ~current
