#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aws_teeスクリプトのテスト
"""

import sys
import importlib.util
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# aws_teeスクリプトをモジュールとして読み込む
aws_tee_path = Path(__file__).parent.parent / "aws_tee"
if not aws_tee_path.exists():
    # Windows環境の場合、拡張子なしファイルの読み込みに対応
    aws_tee_path = Path(__file__).parent.parent / "aws_tee.py"
    if not aws_tee_path.exists():
        # ファイルが存在しない場合は、aws_teeを直接読み込む
        aws_tee_path = Path(__file__).parent.parent / "aws_tee"

spec = importlib.util.spec_from_file_location("aws_tee_module", str(aws_tee_path))
if spec is None or spec.loader is None:
    # フォールバック: ファイルを直接読み込む
    with open(aws_tee_path, "r", encoding="utf-8") as f:
        code = compile(f.read(), str(aws_tee_path), "exec")
        aws_tee = type(sys)("aws_tee_module")
        aws_tee.__file__ = str(aws_tee_path)
        exec(code, aws_tee.__dict__)
else:
    aws_tee = importlib.util.module_from_spec(spec)
    aws_tee.__file__ = str(aws_tee_path)
    sys.modules["aws_tee_module"] = aws_tee
    spec.loader.exec_module(aws_tee)

parse_args = aws_tee.parse_args
main = aws_tee.main


def test_parse_args_with_command_name():
    """コマンド名を指定した場合の引数解析テスト"""
    args = parse_args(["test_command"])
    assert args.command_name == "test_command"


def test_parse_args_without_command_name():
    """コマンド名を指定しなかった場合の引数解析テスト"""
    args = parse_args([])
    assert args.command_name is None


def test_parse_args_help():
    """ヘルプオプションのテスト"""
    with pytest.raises(SystemExit):
        parse_args(["--help"])


def test_main_with_mock():
    """main関数のモックテスト"""
    # モジュール内のクラスを直接パッチ
    with patch.object(aws_tee, "CloudWatchLogsLoggerContext") as mock_cw_logger, \
         patch.object(aws_tee, "S3Stream") as mock_s3_stream, \
         patch.object(aws_tee, "EnvConfigLoader") as mock_env_loader:
        
        # モックの設定
        mock_config = {
            "LOG_GROUP_NAME": "test-log-group",
            "LOG_STREAM_NAME": "test-stream",
            "S3_BUCKET_NAME": "test-bucket",
            "S3_KEY_BASE": "logs/test",
            "S3_SUFFIX": ".log",
        }
        mock_env_loader.load.return_value = {}
        mock_env_loader.resolve.return_value = mock_config

        mock_s3_stream_instance = MagicMock()
        mock_s3_stream_instance.pipe = MagicMock()
        mock_s3_stream.return_value.__enter__.return_value = mock_s3_stream_instance
        mock_s3_stream.return_value.__exit__.return_value = False

        mock_cw_logger_instance = MagicMock()
        mock_cw_logger.return_value.__enter__.return_value = mock_cw_logger_instance
        mock_cw_logger.return_value.__exit__.return_value = False

        # 標準入力をモック
        mock_stdin = MagicMock()
        mock_stdin.buffer = []
        with patch("sys.stdin", mock_stdin):
            # コマンド名を指定して実行
            main(["test_cmd"])

        # モックが呼ばれたことを確認
        mock_env_loader.load.assert_called_once()
        mock_env_loader.resolve.assert_called_once()
        mock_cw_logger.assert_called_once()
        mock_s3_stream.assert_called_once()

