#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
インポートテスト: PyPIパッケージから正しくインポートできることを確認
"""

import pytest


def test_import_env_config_loader():
    """EnvConfigLoaderのインポートテスト"""
    from cloudwatchlogs_s3_stream_descriptor.env_config_loader import EnvConfigLoader
    assert EnvConfigLoader is not None


def test_import_cloud_watch_logs_logger():
    """CloudWatchLogsLoggerContextのインポートテスト"""
    from cloudwatchlogs_s3_stream_descriptor.cloud_watch.cloud_watch_logs_logger import (
        CloudWatchLogsLoggerContext,
    )
    assert CloudWatchLogsLoggerContext is not None


def test_import_s3_stream():
    """S3Streamのインポートテスト"""
    from cloudwatchlogs_s3_stream_descriptor.s3.s3_stream import S3Stream
    assert S3Stream is not None


def test_import_cloud_watch_s3_stream():
    """StanderdStreamCloudWatchS3Senderのインポートテスト"""
    from cloudwatchlogs_s3_stream_descriptor.cloud_watch_s3_stream import (
        StanderdStreamCloudWatchS3Sender,
    )
    assert StanderdStreamCloudWatchS3Sender is not None


def test_import_cloud_watch_s3_logs_context():
    """CloudWatchS3LogsContextのインポートテスト"""
    from cloudwatchlogs_s3_stream_descriptor.cloud_watch_s3_logs_context import (
        CloudWatchS3LogsContext,
    )
    assert CloudWatchS3LogsContext is not None


def test_import_cloud_watch_s3_subprocess():
    """run_command_with_cloud_watch_s3のインポートテスト"""
    from cloudwatchlogs_s3_stream_descriptor.cloud_watch_s3_subprocess import (
        run_command_with_cloud_watch_s3,
    )
    assert run_command_with_cloud_watch_s3 is not None

