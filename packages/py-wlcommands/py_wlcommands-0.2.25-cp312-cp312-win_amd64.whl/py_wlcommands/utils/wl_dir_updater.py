#!/usr/bin/env python3
"""
Utility for checking and updating the .wl directory based on version compatibility.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Optional

from .config import get_config_manager
from .logging import log_info
from .platform_adapter import PlatformAdapter


def check_and_update_wl_dir() -> None:
    """
    Check if .wl directory version is compatible with current wl version.
    If not, update the .wl directory.
    """
    from py_wlcommands import __version__

    # Get current wl version
    current_version = __version__

    # Check if .wl directory exists
    wl_dir = Path(".wl")
    if not wl_dir.exists():
        # No .wl directory, no need to update
        return

    # Check if config.json exists
    config_file = wl_dir / "config.json"
    if not config_file.exists():
        # No config.json, update .wl directory
        log_info("Updating .wl directory (missing config.json)...")
        log_info("正在更新 .wl 目录（缺少 config.json）...", lang="zh")
        _update_wl_directory()
        return

    try:
        # Read current .wl version from config.json
        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)

        wl_dir_version = config.get("version")
        if not wl_dir_version:
            # No version in config, update .wl directory
            log_info("Updating .wl directory (missing version in config)...")
            log_info("正在更新 .wl 目录（配置中缺少版本）...", lang="zh")
            _update_wl_directory()
            return

        # Compare versions
        if _compare_versions(wl_dir_version, current_version) < 0:
            # .wl directory version is older, update it
            log_info(
                f"Updating .wl directory from version {wl_dir_version} to {current_version}..."
            )
            log_info(
                f"正在将 .wl 目录从版本 {wl_dir_version} 更新到 {current_version}...",
                lang="zh",
            )
            _update_wl_directory()

    except (json.JSONDecodeError, OSError) as e:
        # Error reading config.json, update .wl directory
        log_info(f"Updating .wl directory (error reading config.json: {e})...")
        log_info(f"正在更新 .wl 目录（读取 config.json 错误：{e}）...", lang="zh")
        _update_wl_directory()


def _compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings.

    Args:
        version1: First version string (e.g., "0.2.24")
        version2: Second version string (e.g., "0.3.0")

    Returns:
        int: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
    """
    try:
        v1_parts = list(map(int, version1.split(".")))
        v2_parts = list(map(int, version2.split(".")))

        # Ensure both versions have the same number of parts
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts += [0] * (max_len - len(v1_parts))
        v2_parts += [0] * (max_len - len(v2_parts))

        for v1, v2 in zip(v1_parts, v2_parts):
            if v1 < v2:
                return -1
            if v1 > v2:
                return 1

        return 0
    except ValueError:
        # If versions are not in correct format, assume they are equal
        return 0


def _update_wl_directory() -> None:
    """
    Update the .wl directory with the latest files from vendors.
    """
    from py_wlcommands.commands.initenv.utils.project_structure.setup_handler import (
        ProjectStructureSetup,
    )

    try:
        # Use the existing ProjectStructureSetup to update .wl directory
        setup_handler = ProjectStructureSetup()

        # Create .wl directory if it doesn't exist
        wl_dir = Path(".wl")
        wl_dir.mkdir(exist_ok=True)

        # Update config.json with current version
        _update_config_version()

        # Update hooks directory
        _update_hooks_directory()

        # Update other .wl files
        setup_handler._generate_wl_configs()

        log_info("✓ .wl directory updated successfully")
        log_info("✓ .wl 目录更新成功", lang="zh")

    except Exception as e:
        log_info(f"Warning: Failed to update .wl directory: {e}")
        log_info(f"警告：更新 .wl 目录失败：{e}", lang="zh")


def _update_config_version() -> None:
    """
    Update the version in config.json.
    """
    from py_wlcommands import __version__

    config_manager = get_config_manager()
    config_manager.set("version", __version__)


def _update_hooks_directory() -> None:
    """
    Update the hooks directory with the latest files from vendors.
    """
    try:
        # Use the existing hook copying logic from hooks_manager
        from py_wlcommands.commands.initenv.utils.project_structure.hooks_manager import (
            _copy_and_configure_hooks,
        )

        # Update hooks directory
        _copy_and_configure_hooks()

    except Exception as e:
        log_info(f"Warning: Failed to update hooks directory: {e}")
        log_info(f"警告：更新钩子目录失败：{e}", lang="zh")
