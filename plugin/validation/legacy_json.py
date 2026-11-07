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
    prepared = _apply_defaults(_prepare_loaded_document(document))
    document = _canonical(prepared)
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

    Relative paths stay exactly as written, so RUBEM resolves them from the
    JSON file's directory, as it does when the model reads the file. The
    file on disk is not rewritten here.

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
        _chmod_umask_friendly(temporary_name)
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
                raise ValueError(
                    f"Conflicting values for {upper}.{key}: {found[key]!r} and {raw!r}"
                )
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


# Keys the RUBEM pydantic model reads as booleans, which the plugin checks
# before validation. The model maps any unrecognized string to ``False``,
# so the plugin rejects them here instead.
_BOOL_KEYS: dict[str, tuple[str, ...]] = {
    "CONSTANTS": ("lai_max_from_table",),
    "GENERATE_FILE": (
        "itp",
        "bfw",
        "srn",
        "eta",
        "lfw",
        "rec",
        "smc",
        "rnf",
        "arn",
        "tss",
    ),
    "RASTER_FILE_FORMAT": ("map_raster_series", "tiff_raster_series"),
}
_TRUE_TOKENS = {"yes", "true", "t", "1"}
_FALSE_TOKENS = {"no", "false", "f", "0"}


def _apply_defaults(document: dict[str, object]) -> dict[str, object]:
    """Fill the keys the plugin knows the model requires but older files omit."""
    prepared: dict[str, object] = {}
    for section, body in document.items():
        prepared[section] = dict(body) if isinstance(body, dict) else body
    for (section, key), default in _DEFAULTS.items():
        body = prepared.get(section)
        if body is None:
            body = {}
            prepared[section] = body
        if isinstance(body, dict) and key not in body:
            body[key] = default
    return prepared


def _reject_unknown_bool_tokens(draft: dict[str, object]) -> None:
    """Raise ``ValueError`` for a boolean field whose token is not recognized."""
    for section, keys in _BOOL_KEYS.items():
        body = draft.get(section)
        if not isinstance(body, dict):
            continue
        for key in keys:
            if key not in body:
                continue
            value = body[key]
            if isinstance(value, bool):
                continue
            if isinstance(value, str):
                token = value.strip().lower()
                if token in _TRUE_TOKENS or token in _FALSE_TOKENS:
                    # Submodule converters do not strip; normalize before validate.
                    body[key] = token
                    continue
            raise ValueError(
                f"{section}.{key} must be a boolean "
                f"(yes/no, true/false, 1/0); got {value!r}"
            )


def _chmod_umask_friendly(path: str) -> None:
    """Best-effort chmod of a new file to ``0o666 & ~umask``.

    :func:`tempfile.mkstemp` creates files with mode ``0o600``. A project
    file written for the modeller should follow the user's umask instead,
    like the rest of the files the plugin creates. Never raises: the mode
    is a convenience, not a correctness requirement.
    """
    try:
        current = os.umask(0)
        os.umask(current)
    except OSError:
        return
    try:
        os.chmod(path, 0o666 & ~current)
    except OSError:
        pass


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
            if folded in cleaned and cleaned[folded] != value:
                raise ValueError(
                    f"Conflicting values for {upper}.{folded}: "
                    f"{cleaned[folded]!r} and {value!r}"
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

    _reject_unknown_bool_tokens(draft)
    try:
        model = ModelConfigurationFile.model_validate(draft)
    except ValidationError as exc:
        raise ValueError(str(exc)) from exc
    return model.model_dump(by_alias=True, exclude_none=True)


def _as_ini_text(value: object) -> str:
    """Store a JSON value in the dialog parser, keeping relative paths verbatim."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "True" if value else "False"
    return repr(value) if isinstance(value, float) else str(value)
