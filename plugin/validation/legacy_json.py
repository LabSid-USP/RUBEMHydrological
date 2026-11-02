"""Read and write the legacy JSON document RUBEM main accepts.

That document is the project file. It has uppercase sections and no ``version``
field. RUBEM ``main`` also accepts format 1.0, which this editor does not
modify. Relative paths stay as written, because RUBEM resolves them from the
JSON file's directory.
"""

from __future__ import annotations

import json
import os
import tempfile
from configparser import ConfigParser
from pathlib import Path

try:
    from .schemas import defaultConfigSchema
except ImportError:
    from schemas import defaultConfigSchema

# Plugin keys that are not model fields. ``demtif`` is renamed, not dropped.
_RENAMES = {("RASTERS", "demtif"): "georeference"}
_OMIT = {("DIRECTORIES", "input")}

# After lowercasing, a few circulating spellings still need a canonical name.
_ALIASES = {
    ("DIRECTORIES", "precipitation"): "prec",
    ("DIRECTORIES", "rain"): "prec",
    ("DIRECTORIES", "lulc"): "landuse",
    ("FILENAME_PREFIXES", "precipitation_prefix"): "prec_prefix",
    ("FILENAME_PREFIXES", "lulc_prefix"): "landuse_prefix",
    ("RASTERS", "sample_locations"): "samples",
    ("TABLES", "rainy_days"): "rainydays",
    ("TABLES", "dg"): "bulk_density",
    ("TABLES", "kr"): "k_sat",
    ("TABLES", "tcc"): "t_fcap",
    ("TABLES", "tsat"): "t_sat",
    ("TABLES", "tw"): "t_wp",
    ("TABLES", "zr"): "rootzone_depth",
    ("TABLES", "kc_min"): "k_c_min",
    ("TABLES", "kcmin"): "k_c_min",
    ("TABLES", "kc_max"): "k_c_max",
    ("TABLES", "kcmax"): "k_c_max",
    ("CALIBRATION", "beta"): "b",
    ("CALIBRATION", "w1"): "w_1",
    ("CALIBRATION", "w2"): "w_2",
    ("CALIBRATION", "w3"): "w_3",
}

_OPTIONAL_PATHS = {
    ("SIM_TIME", "alignment"),
    ("RASTERS", "ldd"),
    ("RASTERS", "samples"),
    ("RASTERS", "georeference"),
    ("TABLES", "lai_max"),
}

_DEFAULTS: dict[tuple[str, str], object] = {
    ("CONSTANTS", "lai_max_from_table"): False,
    ("GENERATE_FILE", "arn"): False,
    ("RASTER_FILE_FORMAT", "no_data_value"): -9999.0,
}

_ORDER: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("SIM_TIME", ("start", "end", "alignment")),
    ("DIRECTORIES", ("output", "etp", "prec", "ndvi", "kp", "landuse")),
    (
        "FILENAME_PREFIXES",
        ("etp_prefix", "prec_prefix", "ndvi_prefix", "kp_prefix", "landuse_prefix"),
    ),
    (
        "RASTERS",
        (
            "dem",
            "clone",
            "ndvi_max",
            "ndvi_min",
            "soil",
            "ldd",
            "samples",
            "georeference",
        ),
    ),
    (
        "TABLES",
        (
            "rainydays",
            "a_i",
            "a_o",
            "a_s",
            "a_v",
            "manning",
            "bulk_density",
            "k_sat",
            "t_fcap",
            "t_sat",
            "t_wp",
            "rootzone_depth",
            "k_c_min",
            "k_c_max",
            "lai_max",
        ),
    ),
    ("GRID", ("grid",)),
    ("CALIBRATION", ("alpha", "b", "w_1", "w_2", "w_3", "rcd", "f", "alpha_gw", "x")),
    ("INITIAL_SOIL_CONDITIONS", ("t_ini", "bfw_ini", "bfw_lim", "s_sat_ini")),
    ("CONSTANTS", ("fpar_max", "fpar_min", "lai_max", "lai_max_from_table", "i_imp")),
    (
        "GENERATE_FILE",
        ("itp", "bfw", "srn", "eta", "lfw", "rec", "smc", "rnf", "arn", "tss"),
    ),
    (
        "RASTER_FILE_FORMAT",
        ("map_raster_series", "tiff_raster_series", "no_data_value"),
    ),
)

_ALLOWED = {section: set(keys) for section, keys in _ORDER}


def legacy_json_document(
    config: ConfigParser,
) -> tuple[dict[str, dict[str, object]], list[str]]:
    """Build the legacy JSON object for ``config``.

    :param config: Project parser. Values are read with ``raw=True``.
    :returns: The document and human-readable diagnostics for keys that were
        renamed, omitted, or ignored.
    :raises ValueError: A required value is missing, a date is not
        ``DD/MM/YYYY``, a number uses a comma decimal or is not numeric, or a
        flag is not a boolean token. The caller has not written a file yet.
    """
    diagnostics: list[str] = []
    normalized = _normalize(config, diagnostics)
    draft = _draft_from_normalized(normalized)
    return _canonical(draft), diagnostics


def config_from_legacy_document(document: dict[str, object]) -> ConfigParser:
    """Load a legacy JSON object into the parser the dialog edits.

    :param document: Parsed JSON object.
    :returns: Parser seeded from the default project, with document values overlaid.
    :raises ValueError: ``document`` is format 1.0 (it has a ``version`` field)
        or is not an object of section objects.
    """
    if not isinstance(document, dict):
        raise ValueError("RUBEM configuration JSON must be an object")
    if "version" in document:
        raise ValueError(
            "Format 1.0 is a different RUBEM document. This plugin edits the "
            "legacy JSON file, which has no version field."
        )
    parser = ConfigParser()
    parser.read_dict(defaultConfigSchema)
    document = _canonical(_prepare_loaded_document(document))
    for section, keys in _ORDER:
        body = document.get(section, {})
        if not isinstance(body, dict):
            raise ValueError(f"{section} must be an object")
        allowed = set(keys)
        for key, value in body.items():
            if key not in allowed:
                continue
            target = "demtif" if section == "RASTERS" and key == "georeference" else key
            parser.set(section, target, _as_ini_text(value))
    return parser


def read_legacy_json(path: Path | str) -> ConfigParser:
    """Read a project file written by :func:`write_legacy_json`.

    :param path: Path to the JSON project.
    :raises ValueError: The file is not legacy JSON.
    """
    source = Path(path)
    with source.open(encoding="utf-8") as handle:
        document = json.load(handle)
    return config_from_legacy_document(document)


def write_legacy_json(config: ConfigParser, destination: Path | str) -> list[str]:
    """Write ``destination`` as legacy JSON, replacing it only after a full dump.

    :param config: Project parser.
    :param destination: Path of the JSON project.
    :returns: Diagnostics from :func:`legacy_json_document`.
    :raises ValueError: The project cannot be exported. ``destination`` is left
        untouched.
    """
    document, diagnostics = legacy_json_document(config)
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(document, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temporary_name, target)
    except Exception:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
        raise
    return diagnostics


def _normalize(
    config: ConfigParser, diagnostics: list[str]
) -> dict[str, dict[str, str]]:
    """Return section to canonical-key to raw value, recording dropped keys."""
    normalized: dict[str, dict[str, str]] = {}
    for section in config.sections():
        upper = section.upper()
        if upper not in _ALLOWED:
            diagnostics.append(f"Ignored unknown section {section}")
            continue
        found: dict[str, str] = {}
        for option in config.options(section):
            raw = config.get(section, option, raw=True)
            key = option.strip().lower()
            if (upper, key) in _OMIT:
                diagnostics.append(f"Omitted plugin-only key {upper}.{key}")
                continue
            key = _RENAMES.get((upper, key), _ALIASES.get((upper, key), key))
            if key in found and found[key] != raw:
                diagnostics.append(
                    f"Kept {upper}.{key}={found[key]!r} and ignored {option}={raw!r}"
                )
                continue
            found[key] = raw
        unknown = sorted(key for key in found if key not in _ALLOWED[upper])
        for key in unknown:
            diagnostics.append(f"Ignored unknown key {upper}.{key}")
            del found[key]
        normalized[upper] = found
    return normalized


def _draft_from_normalized(
    normalized: dict[str, dict[str, str]],
) -> dict[str, dict[str, object]]:
    """Build the object the RUBEM pydantic model validates.

    Values stay in the spelling the dialog stored. The model coerces dates,
    numbers and booleans. Empty optional paths are left out so the model
    applies its own defaults.
    """
    draft: dict[str, dict[str, object]] = {}
    for section, keys in _ORDER:
        present = normalized.get(section, {})
        body: dict[str, object] = {}
        for key in keys:
            pair = (section, key)
            if key in present:
                raw = present[key]
                if pair in _OPTIONAL_PATHS and raw.strip() == "":
                    continue
                body[key] = raw
            elif pair in _DEFAULTS:
                body[key] = _DEFAULTS[pair]
        draft[section] = body
    return draft


def _prepare_loaded_document(document: dict[str, object]) -> dict[str, object]:
    """Rename plugin spellings before the model sees a loaded JSON object."""
    prepared: dict[str, object] = {}
    for section, body in document.items():
        if not isinstance(body, dict):
            prepared[section] = body
            continue
        upper = str(section).upper()
        cleaned: dict[str, object] = {}
        for key, value in body.items():
            folded = str(key).lower()
            if (upper, folded) in _OMIT:
                continue
            folded = _RENAMES.get(
                (upper, folded), _ALIASES.get((upper, folded), folded)
            )
            cleaned[folded] = value
        prepared[upper] = cleaned
    return prepared


def _canonical(draft: dict[str, object]) -> dict[str, dict[str, object]]:
    """Validate ``draft`` with the submodule's legacy pydantic model."""
    try:
        from ..dependencies import ensure_pydantic
        from ..engine import ensure_submodule_on_path
    except ImportError:
        from dependencies import ensure_pydantic
        from engine import ensure_submodule_on_path

    ensure_pydantic()
    ensure_submodule_on_path()
    from pydantic import ValidationError
    from rubem.configuration.model_configuration_file import ModelConfigurationFile

    try:
        model = ModelConfigurationFile.model_validate(draft)
    except ValidationError as exc:
        raise ValueError(str(exc)) from exc
    return model.model_dump(by_alias=True, exclude_none=True)


def _as_ini_text(value: object) -> str:
    """Store a JSON value in the dialog parser."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)
