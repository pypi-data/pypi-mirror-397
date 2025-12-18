# CloudWatchLogs-S3-Stream-Descriptor

AWS CloudWatch LogsとS3へのストリーム出力を行うPythonライブラリ

## 概要

このライブラリは、Pythonアプリケーションの標準出力・標準エラー出力をAWS CloudWatch LogsやS3にリアルタイムで送信するためのツールです。ログ出力のコンテキストマネージャーやサブプロセスの出力リダイレクトをサポートしています。

## インストール

### pipを使用する場合

```bash
pip install cloudwatchlogs-s3-stream-descriptor
```

### ソースからインストールする場合

```bash
git clone https://github.com/h10x64/CloudWatchLogs-S3-Stream-Descriptor.git
cd CloudWatchLogs-S3-Stream-Descriptor
pip install -e .
```

## 必要な環境

- Python 3.7以上
- AWS認証情報（環境変数、IAMロール、または認証情報ファイル）
- 適切なIAM権限（後述）

## 依存関係

- boto3 >= 1.26.0
- python-dotenv >= 0.19.0

## 基本的な使い方

### 1. CloudWatch LogsとS3の両方にログを出力する

```python
from cloudwatchlogs_s3_stream_descriptor import CloudWatchS3LogsContext

with CloudWatchS3LogsContext(
    log_group_name="my-log-group",
    log_stream_name="my-log-stream",
    bucket_name="my-bucket",
    key="logs/process",
    name="my_process"
) as logger:
    logger.info("Hello, World!")
    logger.warning("This is a warning")
    logger.error("This is an error")
```

### 2. 標準出力・標準エラー出力をCloudWatch LogsとS3にリダイレクトする

```python
import subprocess
from cloudwatchlogs_s3_stream_descriptor import StanderdStreamCloudWatchS3Sender

with StanderdStreamCloudWatchS3Sender(
    log_group_name="my-log-group",
    log_stream_name="my-log-stream",
    bucket_name="my-bucket",
    key="output/script",
    suffix=".log",
) as stream:
    # サブプロセスの標準出力と標準エラー出力をリダイレクト
    process = subprocess.Popen(
        ["python", "script.py"],
        stdout=stream.stdout,
        stderr=stream.stderr,
        text=True
    )
    process.wait()
```

### 3. サブプロセスを実行する（簡易版）

```python
from cloudwatchlogs_s3_stream_descriptor import (
    CloudWatchS3LogsContext,
    run_command_with_cloud_watch_s3
)

with CloudWatchS3LogsContext(
    log_group_name="my-log-group",
    log_stream_name="my-log-stream",
    bucket_name="my-bucket",
    key="logs/main",
    name="main_process"
) as parent:
    # サブプロセスを実行
    return_code = run_command_with_cloud_watch_s3(
        parent=parent,
        name="subprocess",
        command=["python", "script.py"],
        s3_suffix=".log"
    )
```

### 4. 環境設定ファイルの読み込み

```python
from pathlib import Path
from cloudwatchlogs_s3_stream_descriptor import EnvConfigLoader

# 設定ファイルを読み込む
config = EnvConfigLoader.load(Path("config.env"))

# プレースホルダを置換して解決
resolved_config = EnvConfigLoader.resolve(
    raw_config=config,
    defaults={"AWS_REGION": "us-east-1"},
    placeholder_keys=["S3_KEY"],  # %YYYYMMDD% などのプレースホルダを置換
)
```

## 必要なIAM権限

このライブラリを使用するには、以下のIAM権限が必要です：

### CloudWatch Logs用の権限

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
        }
    ]
}
```

### S3用の権限

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:AbortMultipartUpload",
                "s3:ListMultipartUploadParts"
            ],
            "Resource": "arn:aws:s3:::bucket-name/*"
        }
    ]
}
```

## 主な機能

- **CloudWatch Logsへのログ出力**: JSON形式で構造化ログを出力
- **S3へのストリーム出力**: リアルタイムでS3にデータを書き込み（マルチパートアップロード対応）
- **階層的なログ管理**: 親子関係を持つログコンテキストで実行単位を管理
- **標準出力・標準エラー出力のリダイレクト**: サブプロセスの出力を自動的にCloudWatch LogsとS3に送信
- **環境設定ファイルの読み込み**: dotenv形式の設定ファイルを読み込み、プレースホルダを置換

## ライセンス

CC0 1.0 Universal (Public Domain Dedication)

詳細は [LICENSE](LICENSE) ファイルを参照してください。

## コントリビューション

プルリクエストやイシューの報告を歓迎します。

## 作者

n_h <h.10x64@gmail.com>

## リンク

- [GitHubリポジトリ](https://github.com/h10x64/CloudWatchLogs-S3-Stream-Descriptor)

---

# CloudWatchLogs-S3-Stream-Descriptor (English)

Python library for streaming output to AWS CloudWatch Logs and S3

## Overview

This library is a tool for sending standard output and standard error output from Python applications to AWS CloudWatch Logs and S3 in real-time. It supports context managers for log output and subprocess output redirection.

## Installation

### Using pip

```bash
pip install cloudwatchlogs-s3-stream-descriptor
```

### Installing from source

```bash
git clone https://github.com/h10x64/CloudWatchLogs-S3-Stream-Descriptor.git
cd CloudWatchLogs-S3-Stream-Descriptor
pip install -e .
```

## Requirements

- Python 3.7 or higher
- AWS credentials (environment variables, IAM roles, or credential files)
- Appropriate IAM permissions (described below)

## Dependencies

- boto3 >= 1.26.0
- python-dotenv >= 0.19.0

## Basic Usage

### 1. Output logs to both CloudWatch Logs and S3

```python
from cloudwatchlogs_s3_stream_descriptor import CloudWatchS3LogsContext

with CloudWatchS3LogsContext(
    log_group_name="my-log-group",
    log_stream_name="my-log-stream",
    bucket_name="my-bucket",
    key="logs/process",
    name="my_process"
) as logger:
    logger.info("Hello, World!")
    logger.warning("This is a warning")
    logger.error("This is an error")
```

### 2. Redirect standard output and standard error to CloudWatch Logs and S3

```python
import subprocess
from cloudwatchlogs_s3_stream_descriptor import StanderdStreamCloudWatchS3Sender

with StanderdStreamCloudWatchS3Sender(
    log_group_name="my-log-group",
    log_stream_name="my-log-stream",
    bucket_name="my-bucket",
    key="output/script",
    suffix=".log",
) as stream:
    # Redirect subprocess standard output and standard error
    process = subprocess.Popen(
        ["python", "script.py"],
        stdout=stream.stdout,
        stderr=stream.stderr,
        text=True
    )
    process.wait()
```

### 3. Execute subprocess (simplified version)

```python
from cloudwatchlogs_s3_stream_descriptor import (
    CloudWatchS3LogsContext,
    run_command_with_cloud_watch_s3
)

with CloudWatchS3LogsContext(
    log_group_name="my-log-group",
    log_stream_name="my-log-stream",
    bucket_name="my-bucket",
    key="logs/main",
    name="main_process"
) as parent:
    # Execute subprocess
    return_code = run_command_with_cloud_watch_s3(
        parent=parent,
        name="subprocess",
        command=["python", "script.py"],
        s3_suffix=".log"
    )
```

### 4. Load environment configuration file

```python
from pathlib import Path
from cloudwatchlogs_s3_stream_descriptor import EnvConfigLoader

# Load configuration file
config = EnvConfigLoader.load(Path("config.env"))

# Resolve with placeholder replacement
resolved_config = EnvConfigLoader.resolve(
    raw_config=config,
    defaults={"AWS_REGION": "us-east-1"},
    placeholder_keys=["S3_KEY"],  # Replace placeholders like %YYYYMMDD%
)
```

## Required IAM Permissions

The following IAM permissions are required to use this library:

### Permissions for CloudWatch Logs

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
        }
    ]
}
```

### Permissions for S3

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:AbortMultipartUpload",
                "s3:ListMultipartUploadParts"
            ],
            "Resource": "arn:aws:s3:::bucket-name/*"
        }
    ]
}
```

## Key Features

- **Log output to CloudWatch Logs**: Output structured logs in JSON format
- **Stream output to S3**: Write data to S3 in real-time (supports multipart upload)
- **Hierarchical log management**: Manage execution units with parent-child log contexts
- **Standard output/error redirection**: Automatically send subprocess output to CloudWatch Logs and S3
- **Environment configuration file loading**: Load dotenv-format configuration files and replace placeholders

## License

CC0 1.0 Universal (Public Domain Dedication)

See the [LICENSE](LICENSE) file for details.

## Contributing

Pull requests and issue reports are welcome.

## Author

n_h <h.10x64@gmail.com>

## Links

- [GitHub Repository](https://github.com/h10x64/CloudWatchLogs-S3-Stream-Descriptor)
