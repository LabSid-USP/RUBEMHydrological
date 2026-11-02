"""Export a plugin project to the legacy JSON RUBEM main accepts.

The INI written by :meth:`saveProject` stays the project file. RUBEM ``main``
rejects every suffix other than ``.json``. This module builds that legacy
document (uppercase sections, no ``version`` field) with the standard library.
Nothing on the Run path calls it yet.
"""

from __future__ import annotations

import json
import os
import tempfile
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path

_DATE_FORMAT = "%d/%m/%Y"

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

_DATES = {("SIM_TIME", "start"), ("SIM_TIME", "end"), ("SIM_TIME", "alignment")}
_BOOLS = {
    ("CONSTANTS", "lai_max_from_table"),
    ("GENERATE_FILE", "itp"),
    ("GENERATE_FILE", "bfw"),
    ("GENERATE_FILE", "srn"),
    ("GENERATE_FILE", "eta"),
    ("GENERATE_FILE", "lfw"),
    ("GENERATE_FILE", "rec"),
    ("GENERATE_FILE", "smc"),
    ("GENERATE_FILE", "rnf"),
    ("GENERATE_FILE", "arn"),
    ("GENERATE_FILE", "tss"),
    ("RASTER_FILE_FORMAT", "map_raster_series"),
    ("RASTER_FILE_FORMAT", "tiff_raster_series"),
}
_FLOATS = {
    ("GRID", "grid"),
    ("CALIBRATION", "alpha"),
    ("CALIBRATION", "b"),
    ("CALIBRATION", "w_1"),
    ("CALIBRATION", "w_2"),
    ("CALIBRATION", "w_3"),
    ("CALIBRATION", "rcd"),
    ("CALIBRATION", "f"),
    ("CALIBRATION", "alpha_gw"),
    ("CALIBRATION", "x"),
    ("INITIAL_SOIL_CONDITIONS", "t_ini"),
    ("INITIAL_SOIL_CONDITIONS", "bfw_ini"),
    ("INITIAL_SOIL_CONDITIONS", "bfw_lim"),
    ("INITIAL_SOIL_CONDITIONS", "s_sat_ini"),
    ("CONSTANTS", "fpar_max"),
    ("CONSTANTS", "fpar_min"),
    ("CONSTANTS", "lai_max"),
    ("CONSTANTS", "i_imp"),
    ("RASTER_FILE_FORMAT", "no_data_value"),
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
    document: dict[str, dict[str, object]] = {}
    for section, keys in _ORDER:
        present = normalized.get(section, {})
        body: dict[str, object] = {}
        for key in keys:
            label = f"{section}.{key}"
            pair = (section, key)
            if key in present:
                body[key] = _convert(pair, present[key], label)
            elif pair in _DEFAULTS:
                body[key] = _DEFAULTS[pair]
            elif pair in _OPTIONAL_PATHS:
                continue
            else:
                raise ValueError(f"Missing {label}")
            if pair in _OPTIONAL_PATHS and body.get(key) in ("", None):
                del body[key]
        document[section] = body
    return document, diagnostics


def write_legacy_json(config: ConfigParser, destination: Path | str) -> list[str]:
    """Write ``destination`` as legacy JSON, replacing it only after a full dump.

    :param config: Project parser.
    :param destination: Path of the ``.rubem.json`` file, normally beside the INI.
        Relative paths inside the document are left unchanged, because RUBEM
        resolves them from the JSON file's directory.
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


def _convert(pair: tuple[str, str], raw: str, label: str) -> object:
    """Convert one raw INI value to the JSON type RUBEM expects."""
    if pair in _OPTIONAL_PATHS and raw.strip() == "":
        return ""
    if pair in _DATES:
        return _parse_date(raw, label)
    if pair in _BOOLS:
        return _parse_bool(raw, label)
    if pair in _FLOATS:
        return _parse_float(raw, label)
    return raw


def _parse_date(raw: str, label: str) -> str:
    text = raw.strip()
    try:
        datetime.strptime(text, _DATE_FORMAT)
    except ValueError as exc:
        raise ValueError(f"{label} must be DD/MM/YYYY, got {raw!r}") from exc
    return text


def _parse_bool(raw: str, label: str) -> bool:
    text = raw.strip().lower()
    if text in {"yes", "true", "t", "1"}:
        return True
    if text in {"no", "false", "f", "0"}:
        return False
    raise ValueError(f"{label} must be a boolean, got {raw!r}")


def _parse_float(raw: str, label: str) -> float:
    text = raw.strip()
    if "," in text:
        raise ValueError(f"{label} must use a '.' decimal separator, got {raw!r}")
    try:
        number = float(text)
    except ValueError as exc:
        raise ValueError(f"{label} is not a decimal number, got {raw!r}") from exc
    if number != number or number in (float("inf"), float("-inf")):
        raise ValueError(f"{label} must be finite, got {raw!r}")
    return number
