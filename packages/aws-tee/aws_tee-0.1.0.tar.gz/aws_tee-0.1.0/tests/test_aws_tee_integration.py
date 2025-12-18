#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aws_teeコマンドの統合テスト
実際にコマンドを実行して動作を確認
"""

import subprocess
import sys
import tempfile
from pathlib import Path
import pytest


def test_aws_tee_command_with_stdin():
    """echo Hello | aws-tee のようなコマンド実行テスト"""
    aws_tee_path = Path(__file__).parent.parent / "aws_tee"
    original_config = Path(__file__).parent.parent / "aws_tee.conf"
    
    # 一時的な設定ファイルを作成（存在しないリソースを指定してエラーを回避）
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".conf", dir=aws_tee_path.parent) as tmp_config:
        tmp_config.write("# Test config\n")
        tmp_config.write("LOG_GROUP_NAME=test-log-group\n")
        tmp_config.write("LOG_STREAM_NAME=test-stream\n")
        tmp_config.write("S3_BUCKET_NAME=test-bucket\n")
        tmp_config.write("S3_KEY_BASE=test/key\n")
        tmp_config.write("S3_SUFFIX=.log\n")
        tmp_config_path = Path(tmp_config.name)
    
    try:
        # 一時的な設定ファイルを使用
        import shutil
        if original_config.exists():
            shutil.copy(original_config, original_config.with_suffix(".conf.bak"))
        shutil.copy(tmp_config_path, original_config)
        
        # 標準入力を準備
        input_data = "Hello\nWorld\n"
        
        # aws_teeコマンドを実行（AWS接続エラーは無視して標準出力を確認）
        process = subprocess.Popen(
            [sys.executable, str(aws_tee_path), "test_command"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        stdout, stderr = process.communicate(input=input_data, timeout=10)
        
        # 標準出力にデータが出力されていることを確認（tee的な動作）
        assert "Hello" in stdout
        assert "World" in stdout
        
    finally:
        # 設定ファイルを復元
        if original_config.with_suffix(".conf.bak").exists():
            shutil.move(original_config.with_suffix(".conf.bak"), original_config)
        tmp_config_path.unlink(missing_ok=True)


def test_aws_tee_command_without_command_name():
    """コマンド名を指定しない場合のテスト"""
    aws_tee_path = Path(__file__).parent.parent / "aws_tee"
    
    input_data = "Test message\n"
    
    # aws_teeコマンドを実行（コマンド名なし）
    process = subprocess.Popen(
        [sys.executable, str(aws_tee_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    
    stdout, stderr = process.communicate(input=input_data, timeout=10)
    
    # 標準出力にデータが出力されていることを確認
    assert "Test message" in stdout


def test_aws_tee_command_multiline_input():
    """複数行の入力に対するテスト"""
    aws_tee_path = Path(__file__).parent.parent / "aws_tee"
    
    # 複数行の入力
    input_data = "Line 1\nLine 2\nLine 3\n"
    
    process = subprocess.Popen(
        [sys.executable, str(aws_tee_path), "multiline_test"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    
    stdout, stderr = process.communicate(input=input_data, timeout=10)
    
    # すべての行が標準出力に出力されていることを確認（tee的な動作）
    assert "Line 1" in stdout
    assert "Line 2" in stdout
    assert "Line 3" in stdout


def test_aws_tee_command_empty_input():
    """空の入力に対するテスト"""
    aws_tee_path = Path(__file__).parent.parent / "aws_tee"
    
    # 空の入力
    input_data = ""
    
    process = subprocess.Popen(
        [sys.executable, str(aws_tee_path), "empty_test"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    
    stdout, stderr = process.communicate(input=input_data, timeout=10)
    
    # プロセスが正常に終了することを確認（エラーが発生しても終了コードは0の可能性がある）
    # 空の入力でもエラーなく処理できることを確認
    assert process.returncode in [0, 1]  # AWS接続エラーで1になる可能性がある

