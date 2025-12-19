"""Configuration template loader and processor.

This module provides utilities for loading and processing configuration templates
from YAML files, replacing placeholders with values from DigitalEmployeeConfiguration objects.

Authors:
    Immanuel Rhesa (immanuel.rhesa@gdplabs.id)

References:
    NONE
"""

import json
import re
from pathlib import Path
from typing import Any

import yaml

from digital_employee_core.configuration.configuration import DigitalEmployeeConfiguration

# Configuration template filenames
MCP_CONFIGS_TEMPLATE = "mcp_configs.yaml"
TOOL_CONFIGS_TEMPLATE = "tool_configs.yaml"


class ConfigTemplateLoader:
    """Loads and processes configuration templates from YAML files.

    This class handles loading YAML configuration templates and replacing
    placeholders with actual values from DigitalEmployeeConfiguration objects.

    Attributes:
        template_dir (Path): Path to the directory containing template files.
    """

    def __init__(self, template_dir: str | Path | None = None):
        """Initialize the ConfigTemplateLoader.

        Args:
            template_dir (str | Path | None, optional): Path to template directory. Defaults to config_templates
                in the package directory.
        """
        if template_dir is None:
            # Default to config_templates directory in the package
            package_dir = Path(__file__).parent.parent
            template_dir = package_dir / "config_templates"

        self.template_dir = Path(template_dir)

    def load_template(self, filename: str) -> dict[str, Any]:
        """Load a YAML template file.

        Args:
            filename (str): Name of the template file (e.g., 'mcp_configs.yaml').

        Returns:
            dict[str, Any]: Dictionary containing the template configuration.

        Raises:
            FileNotFoundError: If the template file does not exist.
        """
        template_path = self.template_dir / filename
        return self.load_template_from_path(template_path)

    def load_template_from_path(self, filepath: str | Path) -> dict[str, Any]:
        """Load a YAML template file from an absolute path.

        Args:
            filepath (str | Path): Absolute path to the template file.

        Returns:
            dict[str, Any]: Dictionary containing the template configuration.

        Raises:
            FileNotFoundError: If the template file does not exist.
        """
        template_path = Path(filepath)
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        with open(template_path) as f:
            return yaml.safe_load(f) or {}

    @staticmethod
    def merge_configs(
        base_config: dict[str, dict[str, Any]],
        additional_config: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """Merge two configuration dictionaries.

        The additional_config will override values in base_config for matching keys.
        New keys in additional_config will be added to the result.
        Performs recursive deep merge for nested dictionaries.

        Args:
            base_config (dict[str, dict[str, Any]]): Base configuration dictionary.
            additional_config (dict[str, dict[str, Any]]): Additional configuration to merge.

        Returns:
            dict[str, dict[str, Any]]: Merged configuration dictionary.
        """

        def _deep_merge(base: dict[str, Any], additional: dict[str, Any]) -> dict[str, Any]:
            """Recursively merge two dictionaries."""
            result = base.copy()
            for key, value in additional.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    # Recursively merge nested dictionaries
                    result[key] = _deep_merge(result[key], value)
                else:
                    # Override or add new key
                    result[key] = value
            return result

        return _deep_merge(base_config, additional_config)

    @staticmethod
    def _is_comma_separated_list(value: str) -> bool:
        """Check if a string should be converted to a list.

        Args:
            value (str): String to check.

        Returns:
            bool: True if the string is a comma-separated list, False otherwise.
        """
        return "," in value and not value.startswith(("[", "{"))

    @staticmethod
    def _parse_json_default(default_value: str) -> Any:
        """Parse a default value string, converting JSON literals to Python objects.

        Args:
            default_value (str): The default value string to parse.

        Returns:
            Any: Parsed Python object (list, dict, etc.) or original string if not valid JSON.
        """
        stripped = default_value.strip()
        if stripped.startswith(("[", "{")):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                return default_value
        return default_value

    @staticmethod
    def _find_placeholder_key(value: str, start_pos: int) -> tuple[str, int] | None:
        """Extract placeholder key from value starting at position.

        Args:
            value (str): String to search in.
            start_pos (int): Position to start searching (should be after ${).

        Returns:
            tuple[str, int] | None: Tuple of (key, end_position) or None if invalid.
        """
        match = re.match(r"[A-Z_0-9]+", value[start_pos:])
        if not match:
            return None

        key = match.group(0)
        return key, start_pos + len(key)

    @staticmethod
    def _find_default_value(value: str, start_pos: int) -> tuple[str, int] | None:
        """Extract default value handling nested braces.

        Args:
            value (str): String to search in.
            start_pos (int): Position to start searching (should be after colon).

        Returns:
            tuple[str, int] | None: Tuple of (default_value, end_position) or None if unmatched braces.
        """
        brace_count = 1
        pos = start_pos

        while pos < len(value) and brace_count > 0:
            if value[pos] == "{":
                brace_count += 1
            elif value[pos] == "}":
                brace_count -= 1
            pos += 1

        if brace_count != 0:
            return None

        return value[start_pos : pos - 1], pos

    @staticmethod
    def _parse_placeholder(value: str, pos: int) -> tuple[str, str, str, int] | None:
        """Parse a placeholder at the given position.

        Args:
            value (str): String containing the placeholder.
            pos (int): Position of ${ in the string.

        Returns:
            tuple[str, str, str, int] | None: Tuple of (full_placeholder, key, default_value, end_pos)
                or None if parsing failed.
        """
        key_result = ConfigTemplateLoader._find_placeholder_key(value, pos + 2)
        if not key_result:
            return None

        placeholder_key, key_end = key_result

        # Check for default value
        if key_end < len(value) and value[key_end] == ":":
            default_result = ConfigTemplateLoader._find_default_value(value, key_end + 1)
            if not default_result:
                return None
            default_value, placeholder_end = default_result
        elif key_end < len(value) and value[key_end] == "}":
            default_value = ""
            placeholder_end = key_end + 1
        else:
            return None  # Invalid format

        full_placeholder = value[pos:placeholder_end]
        return full_placeholder, placeholder_key, default_value, placeholder_end

    @staticmethod
    def _get_replacement_value(
        placeholder_key: str, default_value: str, config_map: dict[str, str]
    ) -> str | dict[str, Any] | list[Any] | None:
        """Get the replacement value for a placeholder.

        Args:
            placeholder_key (str): The placeholder key to look up.
            default_value (str): The default value if key not in config_map.
            config_map (dict[str, str]): Mapping of keys to values.

        Returns:
            str | dict[str, Any] | list[Any] | None: Replacement value or None if placeholder should be kept.
        """
        if placeholder_key in config_map:
            return config_map[placeholder_key]
        elif default_value != "":
            return ConfigTemplateLoader._parse_json_default(default_value)
        return None

    @staticmethod
    def _replace_placeholders_in_string(value: str, config_map: dict[str, str]) -> str | list[str] | dict[str, Any]:
        """Replace placeholders in a string value with support for default values.

        Placeholders can have the format:
        - ${PLACEHOLDER_KEY}: Simple placeholder, must exist in config_map
        - ${PLACEHOLDER_KEY:default_value}: Placeholder with default, uses default if key not in config_map

        Default values that look like JSON ([], {}) will be parsed into Python objects.

        Args:
            value (str): String containing placeholders.
            config_map (dict[str, str]): Mapping of placeholder keys to values.

        Returns:
            str | list[str] | dict[str, Any]: String with placeholders replaced, list if comma-separated,
                or dict/list if default value was JSON.
        """
        result = value
        pos = 0

        while pos < len(result):
            if result[pos : pos + 2] != "${":
                pos += 1
                continue

            parsed = ConfigTemplateLoader._parse_placeholder(result, pos)
            if not parsed:
                pos += 1
                continue

            full_placeholder, placeholder_key, default_value, placeholder_end = parsed

            replacement = ConfigTemplateLoader._get_replacement_value(placeholder_key, default_value, config_map)

            if replacement is None:
                pos = placeholder_end
                continue

            if result.strip() == full_placeholder and not isinstance(replacement, str):
                return replacement

            replacement_str = str(replacement) if not isinstance(replacement, str) else replacement

            result = result[:pos] + replacement_str + result[placeholder_end:]
            pos = pos + len(replacement_str)

        if ConfigTemplateLoader._is_comma_separated_list(result):
            return [item.strip() for item in result.split(",") if item.strip()]

        return result

    def _replace_placeholders(
        self,
        template: dict[str, Any],
        configurations: list[DigitalEmployeeConfiguration],
    ) -> dict[str, Any]:
        """Replace placeholders in template with configuration values.

        Placeholders are in format ${PLACEHOLDER_KEY} and are replaced with
        values from DigitalEmployeeConfiguration objects matching the key.

        Args:
            template (dict[str, Any]): Template dictionary with placeholders.
            configurations (list[DigitalEmployeeConfiguration]): List of DigitalEmployeeConfiguration objects.

        Returns:
            dict[str, Any]: Dictionary with placeholders replaced by actual values.
        """
        config_map: dict[str, str] = {}
        for config in configurations:
            config_map[config.key] = config.value

        def replace_value(value: Any) -> Any:
            """Recursively replace placeholders in values.

            Args:
                value (Any): Value to process (string, dict, list, or other type).

            Returns:
                Any: Processed value with placeholders replaced. Returns string or list for string inputs,
                    dict for dict inputs, list for list inputs, or the original value for other types.
            """
            if isinstance(value, str):
                replaced = self._replace_placeholders_in_string(value, config_map)
                # Recurse into dict/list defaults to replace nested placeholders
                if isinstance(replaced, (dict, list)):
                    return replace_value(replaced)
                return replaced
            elif isinstance(value, dict):
                return {k: replace_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [replace_value(item) for item in value]
            else:
                return value

        return replace_value(template)

    def load_mcp_configs(
        self,
        configurations: list[DigitalEmployeeConfiguration],
    ) -> dict[str, dict[str, Any]]:
        """Load MCP configuration template and replace placeholders.

        Args:
            configurations (list[DigitalEmployeeConfiguration]): List of DigitalEmployeeConfiguration objects.

        Returns:
            dict[str, dict[str, Any]]: Dictionary mapping MCP names to their configurations.
        """
        template = self.load_template(MCP_CONFIGS_TEMPLATE)
        return self._replace_placeholders(template, configurations)

    def load_tool_configs(
        self,
        configurations: list[DigitalEmployeeConfiguration],
    ) -> dict[str, dict[str, Any]]:
        """Load tool configuration template and replace placeholders.

        Args:
            configurations (list[DigitalEmployeeConfiguration]): List of DigitalEmployeeConfiguration objects.

        Returns:
            dict[str, dict[str, Any]]: Dictionary mapping tool names to their configurations.
        """
        template = self.load_template(TOOL_CONFIGS_TEMPLATE)
        return self._replace_placeholders(template, configurations)
