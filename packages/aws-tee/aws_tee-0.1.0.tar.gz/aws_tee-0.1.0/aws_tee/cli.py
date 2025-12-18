#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aws_tee: 標準入力をそのまま標準出力に流しつつ、
同じ内容を CloudWatch Logs と S3 に送る tee 風コマンド。

使い方:

    somecmd | aws-tee my_command_name

- 設定は同じディレクトリの `aws_tee.conf`（dotenv形式）から読み込む。
- S3 のキーには `S3_KEY_BASE` を使い、`%CMD_NAME%` プレースホルダを
  実行時に指定されたコマンド名で置換する。
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

from cloudwatchlogs_s3_stream_descriptor.env_config_loader import EnvConfigLoader
from cloudwatchlogs_s3_stream_descriptor.cloud_watch.cloud_watch_logs_logger import CloudWatchLogsLoggerContext
from cloudwatchlogs_s3_stream_descriptor.s3.s3_stream import S3Stream


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="aws-tee",
        description="stdin を標準出力に流しつつ CloudWatch Logs / S3 にも保存する tee 風コマンド",
    )
    parser.add_argument(
        "command_name",
        nargs="?",
        help="論理コマンド名（S3キーの%%CMD_NAME%%などに使用）",
    )
    return parser.parse_args(argv)


def main():
    """メインエントリーポイント"""
    try:
        _main()
    except KeyboardInterrupt:
        # パイプ途中での Ctrl+C 等は静かに終了
        sys.exit(130)


def _main(argv=None):
    """メイン処理（テスト用にargvを受け取れる）"""
    args = parse_args(argv or sys.argv[1:])
    cmd_name = args.command_name or "unknown"

    # 設定ファイルのパスを決定
    # 1. カレントディレクトリの aws_tee.conf
    # 2. ホームディレクトリの .aws-tee.conf
    # 3. パッケージディレクトリの aws_tee.conf.example（デフォルト値として）
    config_path = None
    current_dir_config = Path.cwd() / "aws_tee.conf"
    home_config = Path.home() / ".aws-tee.conf"
    package_dir = Path(__file__).parent
    package_config = package_dir / "aws_tee.conf.example"

    if current_dir_config.exists():
        config_path = current_dir_config
    elif home_config.exists():
        config_path = home_config
    elif package_config.exists():
        config_path = package_config

    # 設定読み込み（リージョン設定と日時プレースホルダ展開を含む）
    raw_config = EnvConfigLoader.load(config_path) if config_path else {}
    config = EnvConfigLoader.resolve(
        raw_config,
        defaults={
            "LOG_GROUP_NAME": "aws-tee-log-group",
            "LOG_STREAM_NAME": "aws-tee-stream-%YYYYMMDDhhmmssSSS%",
            "S3_BUCKET_NAME": "aws-tee-bucket",
            "S3_KEY_BASE": "logs/%YYYYMMDD%/aws_tee/%CMD_NAME%",
            "S3_SUFFIX": ".log",
        },
        placeholder_keys={"LOG_STREAM_NAME", "S3_KEY_BASE"},
        now=datetime.now(),
    )

    log_group_name = config["LOG_GROUP_NAME"]
    log_stream_name = config["LOG_STREAM_NAME"]
    bucket_name = config["S3_BUCKET_NAME"]
    s3_key_base = config["S3_KEY_BASE"]
    s3_suffix = config["S3_SUFFIX"]

    # S3_KEY_BASE 内の %CMD_NAME% を実行時コマンド名で置換
    s3_key_base = s3_key_base.replace("%CMD_NAME%", cmd_name)

    # CloudWatch Logs 用ロガー
    cw_logger = CloudWatchLogsLoggerContext(
        parent=None,
        log_group_name=log_group_name,
        log_stream_name=log_stream_name,
        name=f"aws_tee.{cmd_name}",
    )

    # CloudWatch ロガーと S3 ストリームを同時に開く
    with cw_logger:
        with S3Stream(
            bucket_name=bucket_name,
            key=s3_key_base,
            encoding="utf-8",
        ) as s3_stream:
            s3_pipe = s3_stream.pipe

            # 標準入力を読みながら tee 的に出力＆送信
            for raw in sys.stdin.buffer:
                # コンソールへそのまま出力
                sys.stdout.buffer.write(raw)
                sys.stdout.buffer.flush()

                # テキストに変換
                text = raw.decode("utf-8", errors="replace")

                # S3 へ追記
                s3_pipe.write(text)

                # CloudWatch Logs にも詳細ログとして出力
                cw_logger.info(
                    {
                        "cmd_name": cmd_name,
                        "line": text.rstrip("\n"),
                    }
                )


if __name__ == "__main__":
    main()

