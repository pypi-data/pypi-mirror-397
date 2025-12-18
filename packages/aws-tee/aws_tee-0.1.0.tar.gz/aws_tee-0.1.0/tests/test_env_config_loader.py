#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EnvConfigLoaderのテスト
"""

import tempfile
from pathlib import Path
from datetime import datetime
import pytest

from cloudwatchlogs_s3_stream_descriptor.env_config_loader import EnvConfigLoader


def test_load_nonexistent_file():
    """存在しないファイルを読み込むテスト"""
    result = EnvConfigLoader.load(Path("/nonexistent/path/config.env"))
    assert result == {}


def test_load_empty_file():
    """空のファイルを読み込むテスト"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
        f.write("")
        temp_path = Path(f.name)

    try:
        result = EnvConfigLoader.load(temp_path)
        assert result == {}
    finally:
        temp_path.unlink()


def test_load_valid_file():
    """有効な設定ファイルを読み込むテスト"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
        f.write("LOG_GROUP_NAME=test-group\n")
        f.write("S3_BUCKET_NAME=test-bucket\n")
        temp_path = Path(f.name)

    try:
        result = EnvConfigLoader.load(temp_path)
        assert "LOG_GROUP_NAME" in result
        assert result["LOG_GROUP_NAME"] == "test-group"
        assert "S3_BUCKET_NAME" in result
        assert result["S3_BUCKET_NAME"] == "test-bucket"
    finally:
        temp_path.unlink()


def test_replace_placeholders():
    """プレースホルダ置換のテスト"""
    now = datetime(2024, 1, 15, 12, 30, 45, 123000)
    result = EnvConfigLoader.replace_placeholders("%YYYYMMDD%", now)
    assert result == "20240115"

    result = EnvConfigLoader.replace_placeholders("%YYYYMMDDhhmmssSSS%", now)
    assert result == "20240115123045123"


def test_resolve_with_defaults():
    """デフォルト値のマージテスト"""
    raw_config = {"LOG_GROUP_NAME": "custom-group"}
    defaults = {
        "LOG_GROUP_NAME": "default-group",
        "S3_BUCKET_NAME": "default-bucket",
    }

    result = EnvConfigLoader.resolve(raw_config, defaults=defaults)
    assert result["LOG_GROUP_NAME"] == "custom-group"  # raw_configが優先
    assert result["S3_BUCKET_NAME"] == "default-bucket"  # デフォルト値が使用


def test_resolve_with_placeholders():
    """プレースホルダ置換を含む解決テスト"""
    now = datetime(2024, 1, 15, 12, 30, 45, 123000)
    raw_config = {"LOG_STREAM_NAME": "stream-%YYYYMMDD%"}
    defaults = {}

    result = EnvConfigLoader.resolve(
        raw_config,
        defaults=defaults,
        placeholder_keys={"LOG_STREAM_NAME"},
        now=now,
    )
    assert result["LOG_STREAM_NAME"] == "stream-20240115"

