# AWS-tee

標準入力をそのまま標準出力に流しつつ、同じ内容を CloudWatch Logs と S3 に送る tee 風コマンド。

## 概要

`aws_tee` は、Unix の `tee` コマンドのように動作し、標準入力を標準出力に表示しながら、同時に AWS の CloudWatch Logs と S3 にも送信します。

```
somecmd | aws_tee my_command_name
```

このコマンドを実行すると：
- 標準入力の内容が標準出力に表示される（tee 的な動作）
- CloudWatch Logs に JSON 形式のログとして送信される
- S3 に生ログとして保存される

## 機能

- **tee 的な動作**: 標準入力を標準出力にも表示
- **CloudWatch Logs への送信**: 1行ごとに JSON 形式のログとして送信
- **S3 への保存**: 生ログを S3 に保存
- **プレースホルダ対応**: 日付やコマンド名を動的に埋め込める
- **自動リソース作成**: ロググループやログストリームが存在しない場合、自動的に作成

## インストール

### 前提条件

- Python 3.7 以上
- AWS 認証情報の設定（環境変数、IAM ロール、または `~/.aws/credentials`）

### PyPIからインストール（推奨）

```bash
pip install aws-tee
```

インストール後、`aws-tee`コマンドがパスの通った場所に配置され、どこからでも実行できます：

```bash
echo "Hello" | aws-tee my_command
```

### 開発環境でのセットアップ

1. リポジトリをクローンまたはダウンロード

2. 仮想環境を作成（推奨）

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 開発モードでインストール

```bash
pip install -e .
```

これにより、開発中のコードがそのまま使えるようになります。

4. 開発用依存関係をインストール（テスト実行時）

```bash
pip install -e ".[dev]"
```

## 使用方法

### 基本的な使い方

PyPIからインストールした場合：

```bash
echo "Hello, World" | aws-tee my_command
```

開発環境で直接実行する場合：

```bash
echo "Hello, World" | python -m aws_tee.cli my_command
```

### パイプと組み合わせる

```bash
# コマンドの出力をログに記録
ls -la | aws_tee list_files

# スクリプトの実行結果をログに記録
python script.py | aws_tee run_script

# 複数行の入力
cat file.txt | aws_tee process_file
```

### コマンド名の指定

コマンド名は省略可能です。省略した場合、`unknown` が使用されます。

コマンド名は以下の用途で使用されます：
- S3 キーの `%CMD_NAME%` プレースホルダに埋め込まれる
- CloudWatch Logs の JSON ログの `cmd_name` フィールドに記録される

```bash
echo "test" | aws_tee        # コマンド名: unknown
echo "test" | aws_tee my_cmd # コマンド名: my_cmd
```

例：`aws_tee backup_script` を実行した場合
- S3 キー: `logs/20241216/aws_tee/backup_script.log`
- CloudWatch Logs: `{"cmd_name": "backup_script", "line": "..."}`

## 設定

設定は `aws_tee.conf` ファイル（dotenv 形式）で行います。`aws_tee` と同じディレクトリに配置してください。ファイルが見つからない場合は、以下の順序で探索します：

1. カレントディレクトリの `aws_tee.conf`
2. ホームディレクトリの `~/.aws-tee.conf`
3. パッケージ同梱の `aws_tee.conf.example`（デフォルト値として使用）

### 設定ファイルの例

```env
# CloudWatch Logs 設定
LOG_GROUP_NAME=aws-tee-log-group
LOG_STREAM_NAME=aws-tee-stream-%YYYYMMDDhhmmssSSS%

# S3 設定
S3_BUCKET_NAME=your-aws-tee-bucket
S3_KEY_BASE=logs/%YYYYMMDD%/aws_tee/%CMD_NAME%
S3_SUFFIX=.log

# AWS リージョン（必須）
AWS_REGION=ap-northeast-1
```

### 設定項目

| 項目 | 説明 | 必須 |
|------|------|------|
| `LOG_GROUP_NAME` | CloudWatch Logs のロググループ名 | いいえ（デフォルト: `aws-tee-log-group`） |
| `LOG_STREAM_NAME` | CloudWatch Logs のログストリーム名 | いいえ（デフォルト: `aws-tee-stream-%YYYYMMDDhhmmssSSS%`） |
| `S3_BUCKET_NAME` | S3 バケット名 | いいえ（デフォルト: `aws-tee-bucket`） |
| `S3_KEY_BASE` | S3 キーのベースパス | いいえ（デフォルト: `logs/%YYYYMMDD%/aws_tee/%CMD_NAME%`） |
| `S3_SUFFIX` | S3 ファイルのサフィックス | いいえ（デフォルト: `.log`） |
| `AWS_REGION` | AWS リージョン | いいえ（環境変数から取得可能） |

### プレースホルダ

設定ファイルでは以下のプレースホルダが使用できます：

- **日時プレースホルダ**:
  - `%YYYY%` - 年（4桁）
  - `%MM%` - 月（2桁）
  - `%DD%` - 日（2桁）
  - `%hh%` - 時（2桁）
  - `%mm%` - 分（2桁）
  - `%ss%` - 秒（2桁）
  - `%SSS%` - ミリ秒（3桁）
  - `%YYYYMMDDhhmmssSSS%` - 完全な日時形式

- **コマンド名プレースホルダ**:
  - `%CMD_NAME%` - 実行時に指定したコマンド名

例：
```env
LOG_STREAM_NAME=aws-tee-stream-%YYYYMMDDhhmmssSSS%
S3_KEY_BASE=logs/%YYYYMMDD%/aws_tee/%CMD_NAME%
```

## 必要な IAM 権限

`aws_tee` を使用するには、以下の IAM 権限が必要です：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:AbortMultipartUpload",
        "s3:ListMultipartUploadParts"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

## 出力形式

### CloudWatch Logs

CloudWatch Logs には、各行が JSON 形式で送信されます：

```json
{
  "cmd_name": "my_command",
  "line": "Hello, World"
}
```

### S3

S3 には、標準入力の内容がそのまま保存されます。ファイル名は以下の形式です：

- 標準出力: `{S3_KEY_BASE}{S3_SUFFIX}`
- 標準エラー出力: `{S3_KEY_BASE}_ERROR{S3_SUFFIX}`

例：
- `logs/20241216/aws_tee/my_command.log`
- `logs/20241216/aws_tee/my_command_ERROR.log`

## テスト

テストスイートを実行するには：

```bash
# 仮想環境をアクティブ化
source venv/bin/activate  # Windows: venv\Scripts\activate

# すべてのテストを実行
pytest tests/ -v

# 特定のテストを実行
pytest tests/test_aws_tee_integration.py -v
```

### テスト内容

- **インポートテスト**: PyPI パッケージからの正しいインポートを確認
- **ユニットテスト**: 各関数の動作を確認
- **統合テスト**: 実際のコマンド実行をテスト（`echo Hello | aws-tee` など）

## 依存関係

- [cloudwatchlogs-s3-stream-descriptor](https://pypi.org/project/cloudwatchlogs-s3-stream-descriptor/) - CloudWatch Logs と S3 へのログ送信機能
- pytest - テストフレームワーク（開発時のみ）

## トラブルシューティング

### AWS 認証エラー

AWS 認証情報が正しく設定されているか確認してください：

```bash
aws configure list
```

または環境変数を設定：

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=ap-northeast-1
```

### リソースが見つからないエラー

ロググループやログストリームが存在しない場合、自動的に作成されます。作成に失敗した場合は、IAM 権限を確認してください。

### 設定ファイルが見つからない

設定ファイルは以下の順序で検索されます：

1. カレントディレクトリの `aws_tee.conf`
2. ホームディレクトリの `~/.aws-tee.conf`
3. パッケージに含まれる `aws_tee.conf.example`（デフォルト値として使用）

いずれかの場所に設定ファイルを作成してください。

## ライセンス

このプロジェクトは CC0 1.0 Universal ライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 貢献

バグ報告や機能要望は、Issue でお知らせください。プルリクエストも歓迎します。

## 作者

n_h <h.10x64@gmail.com>

## 関連プロジェクト

- [cloudwatchlogs-s3-stream-descriptor](https://pypi.org/project/cloudwatchlogs-s3-stream-descriptor/) - このプロジェクトが依存する PyPI パッケージ

---

# AWS-tee (English)

A tee-like command that streams standard input to standard output while simultaneously sending the same content to CloudWatch Logs and S3.

## Overview

`aws-tee` works like Unix's `tee` command, displaying standard input to standard output while simultaneously sending it to AWS CloudWatch Logs and S3.

```
somecmd | aws-tee my_command_name
```

When you run this command:
- The content of standard input is displayed to standard output (tee-like behavior)
- It is sent to CloudWatch Logs as JSON-formatted logs
- It is saved as raw logs to S3

## Features

- **Tee-like behavior**: Displays standard input to standard output
- **CloudWatch Logs integration**: Sends logs in JSON format line by line
- **S3 storage**: Saves raw logs to S3
- **Placeholder support**: Dynamically embed dates and command names
- **Automatic resource creation**: Automatically creates log groups and log streams if they don't exist

## Installation

### Prerequisites

- Python 3.7 or higher
- AWS credentials configured (environment variables, IAM role, or `~/.aws/credentials`)

### Install from PyPI (Recommended)

```bash
pip install aws-tee
```

After installation, the `aws-tee` command will be available in your PATH and can be executed from anywhere:

```bash
echo "Hello" | aws-tee my_command
```

### Development Setup

1. Clone or download the repository

2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install in development mode

```bash
pip install -e .
```

This allows you to use the code as you develop it.

4. Install development dependencies (for running tests)

```bash
pip install -e ".[dev]"
```

## Usage

### Basic Usage

If installed from PyPI:

```bash
echo "Hello, World" | aws-tee my_command
```

If running directly in a development environment:

```bash
echo "Hello, World" | python -m aws_tee.cli my_command
```

### Using with Pipes

```bash
# Log command output
ls -la | aws-tee list_files

# Log script execution results
python script.py | aws-tee run_script

# Multiple lines of input
cat file.txt | aws-tee process_file
```

### Command Name Specification

The command name is optional. If omitted, `unknown` will be used.

The command name is used for the following purposes:
- Embedded in the `%CMD_NAME%` placeholder in S3 keys
- Recorded in the `cmd_name` field of CloudWatch Logs JSON logs

```bash
echo "test" | aws-tee        # Command name: unknown
echo "test" | aws-tee my_cmd # Command name: my_cmd
```

Example: When running `aws-tee backup_script`
- S3 key: `logs/20241216/aws_tee/backup_script.log`
- CloudWatch Logs: `{"cmd_name": "backup_script", "line": "..."}`

## Configuration

Configuration is done via the `aws_tee.conf` file (dotenv format). Place it in the same directory as `aws-tee`. If the file is not found, it is searched in this order:

1. `aws_tee.conf` in the current directory
2. `~/.aws-tee.conf` in the home directory
3. `aws_tee.conf.example` bundled in the package (used as default values)

### Configuration File Example

```env
# CloudWatch Logs settings
LOG_GROUP_NAME=aws-tee-log-group
LOG_STREAM_NAME=aws-tee-stream-%YYYYMMDDhhmmssSSS%

# S3 settings
S3_BUCKET_NAME=your-aws-tee-bucket
S3_KEY_BASE=logs/%YYYYMMDD%/aws_tee/%CMD_NAME%
S3_SUFFIX=.log

# AWS Region (required)
AWS_REGION=ap-northeast-1
```

### Configuration Items

| Item | Description | Required |
|------|-------------|----------|
| `LOG_GROUP_NAME` | CloudWatch Logs log group name | No (default: `aws-tee-log-group`) |
| `LOG_STREAM_NAME` | CloudWatch Logs log stream name | No (default: `aws-tee-stream-%YYYYMMDDhhmmssSSS%`) |
| `S3_BUCKET_NAME` | S3 bucket name | No (default: `aws-tee-bucket`) |
| `S3_KEY_BASE` | S3 key base path | No (default: `logs/%YYYYMMDD%/aws_tee/%CMD_NAME%`) |
| `S3_SUFFIX` | S3 file suffix | No (default: `.log`) |
| `AWS_REGION` | AWS region | No (can be obtained from environment variables) |

### Placeholders

The following placeholders can be used in the configuration file:

- **Date/Time placeholders**:
  - `%YYYY%` - Year (4 digits)
  - `%MM%` - Month (2 digits)
  - `%DD%` - Day (2 digits)
  - `%hh%` - Hour (2 digits)
  - `%mm%` - Minute (2 digits)
  - `%ss%` - Second (2 digits)
  - `%SSS%` - Milliseconds (3 digits)
  - `%YYYYMMDDhhmmssSSS%` - Complete datetime format

- **Command name placeholder**:
  - `%CMD_NAME%` - Command name specified at runtime

Example:
```env
LOG_STREAM_NAME=aws-tee-stream-%YYYYMMDDhhmmssSSS%
S3_KEY_BASE=logs/%YYYYMMDD%/aws_tee/%CMD_NAME%
```

## Required IAM Permissions

The following IAM permissions are required to use `aws-tee`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:AbortMultipartUpload",
        "s3:ListMultipartUploadParts"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

## Output Format

### CloudWatch Logs

Each line is sent to CloudWatch Logs in JSON format:

```json
{
  "cmd_name": "my_command",
  "line": "Hello, World"
}
```

### S3

The content of standard input is saved to S3 as-is. File names follow this format:

- Standard output: `{S3_KEY_BASE}{S3_SUFFIX}`
- Standard error output: `{S3_KEY_BASE}_ERROR{S3_SUFFIX}`

Example:
- `logs/20241216/aws_tee/my_command.log`
- `logs/20241216/aws_tee/my_command_ERROR.log`

## Testing

To run the test suite:

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run all tests
pytest tests/ -v

# Run specific tests
pytest tests/test_aws_tee_integration.py -v
```

### Test Coverage

- **Import tests**: Verify correct imports from PyPI package
- **Unit tests**: Verify behavior of each function
- **Integration tests**: Test actual command execution (e.g., `echo Hello | aws-tee`)

## Dependencies

- [cloudwatchlogs-s3-stream-descriptor](https://pypi.org/project/cloudwatchlogs-s3-stream-descriptor/) - Logging functionality for CloudWatch Logs and S3
- pytest - Test framework (development only)

## Troubleshooting

### AWS Authentication Error

Verify that AWS credentials are correctly configured:

```bash
aws configure list
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=ap-northeast-1
```

### Resource Not Found Error

If log groups or log streams don't exist, they will be created automatically. If creation fails, check IAM permissions.

### Configuration File Not Found

Configuration files are searched in the following order:

1. `aws_tee.conf` in the current directory
2. `~/.aws-tee.conf` in the home directory
3. `aws_tee.conf.example` included in the package (used as default values)

Create a configuration file in one of these locations.

## License

This project is released under the CC0 1.0 Universal license. See the [LICENSE](LICENSE) file for details.

## Contributing

Please report bugs and feature requests via Issues. Pull requests are also welcome.

## Author

n_h <h.10x64@gmail.com>

## Related Projects

- [cloudwatchlogs-s3-stream-descriptor](https://pypi.org/project/cloudwatchlogs-s3-stream-descriptor/) - PyPI package that this project depends on

