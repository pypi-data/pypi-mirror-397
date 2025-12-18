#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CloudWatch Logs + S3 に標準出力・標準エラーを流し込みながら
サブプロセスを実行するためのユーティリティ。

`_tool_/test/test.py` の run_test_script / run_error_script でやっている
「コンテキスト作成 → センダー作成 → subprocess 実行 → wait → 終了コード返却」
という流れを汎用化する。
"""

import subprocess
from typing import Sequence, List

from .cloud_watch_s3_logs_context import CloudWatchS3LogsContext
from .cloud_watch_s3_stream import StanderdStreamCloudWatchS3Sender


def run_command_with_cloud_watch_s3(
    *,
    parent: CloudWatchS3LogsContext,
    name: str,
    command: Sequence[str],
    s3_suffix: str,
) -> int:
    """
    CloudWatchS3LogsContext と StanderdStreamCloudWatchS3Sender を使って
    サブプロセスを実行し、終了コードを返すユーティリティ。

    Args:
        parent: 親の CloudWatchS3LogsContext
        name: 子コンテキストの名前（ログ上の識別用）
        command: subprocess.Popen に渡すコマンド（["bash", "script.sh"] など）
        s3_suffix: S3 出力ファイルのサフィックス（例: ".log"）

    Returns:
        サブプロセスの終了コード
    """
    cmd_list: List[str] = list(command)

    # 子コンテキストを作成
    with CloudWatchS3LogsContext(
        parent=parent,
        name=name,
    ) as logger:
        logger.info(f"サブプロセスの実行を開始します: command={cmd_list}")
        print(f"[DEBUG] サブプロセスの実行を開始します: command={cmd_list}")

        # CloudWatch Logs と S3 に出力するストリームを作成
        with StanderdStreamCloudWatchS3Sender(
            log_group_name=logger.log_group_name,
            log_stream_name=logger.log_stream_name,
            bucket_name=logger.bucket_name,
            key=logger.key,
            suffix=s3_suffix,
        ) as stream:
            print("[DEBUG] ストリーム作成完了")

            process = subprocess.Popen(
                cmd_list,
                stdout=stream.stdout,
                stderr=stream.stderr,
            )
            print(f"[DEBUG] サブプロセス開始: PID={process.pid}")

            print("[DEBUG] サブプロセスの完了を待機中...")
            return_code = process.wait()
            print(f"[DEBUG] サブプロセス完了: 終了コード={return_code}")

            if return_code != 0:
                logger.error(f"サブプロセスがエラーで終了しました。終了コード: {return_code}")
            else:
                logger.info(f"サブプロセスの実行が完了しました。終了コード: {return_code}")

            return return_code


