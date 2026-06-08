from __future__ import annotations

import ast
import shlex
import subprocess
import sys
from pathlib import Path
from shutil import which

from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError


MEDIA_KEYS_SCHEMA = "org.gnome.settings-daemon.plugins.media-keys"
SHORTCUT_BASE_PATH = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"
SELECTED_TEXT_SHORTCUT_PATH = (
    "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"
    "so-intelligence-tools-selected-text-correction/"
)


class GnomeShortcutManager:
    def __init__(
        self,
        *,
        python_executable: str | None = None,
        gsettings_bin: str | None = None,
    ) -> None:
        self._python_executable = python_executable or sys.executable
        self._gsettings_bin = gsettings_bin or self._detect_gsettings_bin()

    def install_selected_text_correction_shortcut(self, *, binding: str, debug: bool = False) -> str:
        command = self._build_selected_text_correction_command(debug=debug)
        current_paths = self._get_custom_keybindings()
        if SELECTED_TEXT_SHORTCUT_PATH not in current_paths:
            current_paths.append(SELECTED_TEXT_SHORTCUT_PATH)
            self._set_custom_keybindings(current_paths)

        schema_with_path = (
            "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:"
            f"{SELECTED_TEXT_SHORTCUT_PATH}"
        )
        self._gsettings("set", schema_with_path, "name", "Selected Text Correction")
        self._gsettings("set", schema_with_path, "command", command)
        self._gsettings("set", schema_with_path, "binding", binding)
        return command

    def _build_selected_text_correction_command(self, *, debug: bool = False) -> str:
        args = ["run-selected-text-correction"]
        if debug:
            args.append("--debug")
        command_suffix = " ".join(shlex.quote(arg) for arg in args)
        script_candidate = Path(sys.prefix) / "bin" / "so-intelligence-tools"
        if script_candidate.exists():
            return f"{shlex.quote(str(script_candidate))} {command_suffix}"
        python_path = Path(self._python_executable).resolve()
        return f"{shlex.quote(str(python_path))} -m so_intelligence_tools {command_suffix}"

    def _get_custom_keybindings(self) -> list[str]:
        raw = self._gsettings("get", MEDIA_KEYS_SCHEMA, "custom-keybindings")
        cleaned = raw.strip()
        if cleaned.startswith("@as "):
            cleaned = cleaned[4:]
        try:
            value = ast.literal_eval(cleaned)
        except (SyntaxError, ValueError) as exc:
            raise ToolRunnerConfigurationError(
                "No se pudo interpretar la lista de atajos personalizados de GNOME."
            ) from exc
        if not isinstance(value, list):
            raise ToolRunnerConfigurationError(
                "GNOME devolvió un formato inesperado para los atajos personalizados."
            )
        return [str(item) for item in value]

    def _set_custom_keybindings(self, paths: list[str]) -> None:
        serialized = "[" + ", ".join(repr(path) for path in paths) + "]"
        self._gsettings("set", MEDIA_KEYS_SCHEMA, "custom-keybindings", serialized)

    def _gsettings(self, action: str, schema: str, key: str, value: str | None = None) -> str:
        command = [self._gsettings_bin, action, schema, key]
        if value is not None:
            if action == "set" and not value.startswith("[") and not value.startswith("'"):
                value = repr(value)
            command.append(value)

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise ToolRunnerConfigurationError(
                f"No se pudo completar la operación de atajos GNOME: {result.stderr.strip() or result.stdout.strip()}"
            )
        return result.stdout.strip()

    @staticmethod
    def _detect_gsettings_bin() -> str:
        # Prefer the system gsettings binary explicitly because some sandboxed
        # environments expose wrappers that report success inconsistently.
        if Path("/usr/bin/gsettings").exists():
            return "/usr/bin/gsettings"
        detected = which("gsettings")
        if detected:
            return detected
        raise ToolRunnerConfigurationError("No se encontró `gsettings` en el sistema.")
