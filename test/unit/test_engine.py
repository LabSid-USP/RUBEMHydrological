"""The model comes from the submodule, not from an executable path."""

from __future__ import annotations

from pathlib import Path

import pytest

from plugin.engine import (
    PCRASTER_TOOLS_ID,
    PCRASTER_TOOLS_URL,
    assert_pcraster_tools,
    assert_ready,
    configure_spawn_executable,
    ensure_submodule_on_path,
    pcraster_tools_message,
    resolve_host_python,
    submodule_path,
)


@pytest.mark.unit
def test_already_imported_old_pydantic_is_not_replaced(monkeypatch) -> None:
    """An incompatible module already in memory is not hidden by another install."""
    import sys
    import types

    from plugin.dependencies import PydanticUnavailable, ensure_pydantic

    original = sys.modules.get("pydantic")
    fake = types.ModuleType("pydantic")
    fake.__version__ = "2.10.0"
    sys.modules["pydantic"] = fake

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("pip must not run when Pydantic is already imported")

    monkeypatch.setattr("plugin.dependencies.subprocess.run", fail_if_called)
    try:
        with pytest.raises(PydanticUnavailable, match="already loaded"):
            ensure_pydantic(install=True)
    finally:
        if original is None:
            sys.modules.pop("pydantic", None)
        else:
            sys.modules["pydantic"] = original


@pytest.mark.unit
def test_pydantic_requirement_rejects_version_3() -> None:
    """The upper bound is exclusive, matching the submodule pin."""
    from plugin.dependencies import pydantic_version_is_supported

    assert pydantic_version_is_supported("2.11.0")
    assert pydantic_version_is_supported("2.14.1")
    assert not pydantic_version_is_supported("2.10.9")
    assert not pydantic_version_is_supported("3.0.0")


@pytest.mark.unit
def test_archive_uses_one_root_and_keeps_runtime_files() -> None:
    """The zip layout matches the directory QGIS imports."""
    from scripts.build_plugin import ARCHIVE_ROOT, archive_member, iter_plugin_files

    root = Path(__file__).resolve().parents[2]
    assert archive_member(root, root / "metadata.txt") == f"{ARCHIVE_ROOT}/metadata.txt"
    assert (
        archive_member(root, root / "plugin" / "engine.py")
        == f"{ARCHIVE_ROOT}/plugin/engine.py"
    )
    names = {archive_member(root, path) for path in iter_plugin_files(root)}
    assert f"{ARCHIVE_ROOT}/plugin/gui/generated/resources.rcc" in names
    assert f"{ARCHIVE_ROOT}/external/rubem-model/rubem/api.py" in names
    assert f"{ARCHIVE_ROOT}/external/rubem-model/rubem/appsettings.json" in names
    assert f"{ARCHIVE_ROOT}/i18n/RUBEMHydrological_en_US.qm" in names
    assert f"{ARCHIVE_ROOT}/i18n/RUBEMHydrological_pt_BR.qm" in names
    assert all(name.startswith(f"{ARCHIVE_ROOT}/") for name in names)


@pytest.mark.unit
def test_installed_pydantic_satisfies_the_submodule_pin() -> None:
    """A usable Pydantic does not trigger another install."""
    from plugin.dependencies import ensure_pydantic

    ensure_pydantic()


@pytest.mark.unit
def test_missing_runtime_extras_prompt_install_when_pydantic_ok(monkeypatch) -> None:
    """Save/open can reach the install path when only humanize/dateutil are missing."""
    from plugin.dependencies import PydanticUnavailable, ensure_pydantic

    monkeypatch.setattr("plugin.dependencies._cached_pydantic_status", lambda: "ok")
    monkeypatch.setattr(
        "plugin.dependencies._activate_existing_environment", lambda: None
    )
    monkeypatch.setattr(
        "plugin.dependencies._pure_python_modules_missing",
        lambda: ["humanize", "dateutil"],
    )
    with pytest.raises(PydanticUnavailable, match="humanize"):
        ensure_pydantic()

    installs: list[bool] = []

    def fake_ensure() -> None:
        installs.append(True)

    monkeypatch.setattr("plugin.dependencies._ensure_isolated_extras", fake_ensure)
    ensure_pydantic(install=True)
    assert installs == [True]


@pytest.mark.unit
def test_submodule_path_is_the_pinned_checkout() -> None:
    """The runner looks at external/rubem-model and nowhere else."""
    path = submodule_path()
    assert path.name == "rubem-model"
    assert path.parent.name == "external"
    assert (path / "rubem" / "api.py").is_file()


@pytest.mark.unit
def test_missing_submodule_is_reported(tmp_path: Path) -> None:
    """A checkout without the package is not treated as an installed command."""
    with pytest.raises(FileNotFoundError, match="git submodule update --init"):
        ensure_submodule_on_path(tmp_path)


@pytest.mark.unit
def test_inactive_pcraster_tools_names_the_plugin_and_refuses_pip() -> None:
    """The message points at the QGIS plugin and does not offer pip."""
    with pytest.raises(RuntimeError, match="PCRaster Tools") as exc:
        assert_pcraster_tools([])
    text = str(exc.value)
    assert PCRASTER_TOOLS_ID in pcraster_tools_message()
    assert PCRASTER_TOOLS_URL in text
    assert "pip" in text
    assert "3.99" in text


@pytest.mark.unit
def test_resolve_host_python_prefers_prefix_over_sibling(tmp_path: Path) -> None:
    """The interpreter owning the stdlib prefix wins over a host sibling."""
    prefix = tmp_path / "prefix"
    prefix.mkdir()
    (prefix / "python.exe").touch()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "python.exe").touch()
    found = resolve_host_python(
        executable=bin_dir / "qgis-bin.exe",
        base_executable="",
        prefixes=[prefix],
        platform="win32",
        version_info=(3, 13),
    )
    assert found == prefix / "python.exe"


@pytest.mark.unit
def test_resolve_host_python_windows_osgeo_exact_version_first(
    tmp_path: Path,
) -> None:
    """OSGeo4W apps/Python<major><minor> beats other Python* directories."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for folder in ("Python312", "Python313"):
        app = tmp_path / "apps" / folder
        app.mkdir(parents=True)
        (app / "python.exe").touch()
    found = resolve_host_python(
        executable=bin_dir / "qgis-bin.exe",
        base_executable="",
        prefixes=[],
        platform="win32",
        version_info=(3, 13),
    )
    assert found == tmp_path / "apps" / "Python313" / "python.exe"


@pytest.mark.unit
def test_resolve_host_python_windows_skips_mismatched_python_apps(
    tmp_path: Path,
) -> None:
    """A Python310 apps folder must not be chosen for a 3.13 host."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for folder in ("Python310", "Python312"):
        app = tmp_path / "apps" / folder
        app.mkdir(parents=True)
        (app / "python.exe").touch()
    found = resolve_host_python(
        executable=bin_dir / "qgis-bin.exe",
        base_executable="",
        prefixes=[],
        platform="win32",
        version_info=(3, 13),
    )
    assert found is None


@pytest.mark.unit
def test_resolve_host_python_posix_sibling_and_none(tmp_path: Path) -> None:
    """A python3 sibling is used on POSIX; no candidate means None."""
    bin_dir = tmp_path / "MacOS"
    bin_dir.mkdir()
    (bin_dir / "python3").touch()
    found = resolve_host_python(
        executable=bin_dir / "QGIS",
        base_executable="",
        prefixes=[],
        platform="darwin",
        version_info=(3, 13),
    )
    assert found == bin_dir / "python3"
    empty = tmp_path / "empty"
    empty.mkdir()
    assert (
        resolve_host_python(
            executable=empty / "qgis",
            base_executable="",
            prefixes=[],
            platform="linux",
            version_info=(3, 13),
        )
        is None
    )


@pytest.mark.unit
def test_configure_spawn_executable_raises_when_host_is_not_python(
    tmp_path: Path, monkeypatch
) -> None:
    """Spawn must not keep qgis-bin when no host Python can be resolved."""
    from plugin import engine as engine_mod

    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr(engine_mod.sys, "executable", str(empty / "qgis-bin"))
    monkeypatch.setattr(
        engine_mod,
        "resolve_host_python",
        lambda **_kwargs: None,
    )
    with pytest.raises(RuntimeError, match="Python interpreter"):
        configure_spawn_executable()


@pytest.mark.unit
def test_ready_check_requires_native_pcraster_not_the_processing_plugin() -> None:
    """QGIS 4 cannot install PCRaster Tools 0.4.0, so the gate is the import."""
    with pytest.raises(ImportError, match="pcraster"):
        assert_ready()
