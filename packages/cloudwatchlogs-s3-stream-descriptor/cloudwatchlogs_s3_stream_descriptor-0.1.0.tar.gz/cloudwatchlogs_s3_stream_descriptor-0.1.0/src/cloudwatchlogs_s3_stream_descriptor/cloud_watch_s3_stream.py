import sys
import threading
from typing import Optional
import os

from .cloud_watch_and_s3_parent import CloudWatchAndS3Parent
from .cloud_watch.standerd_stream_cloud_watch_logs_sender import StanderdStreamCloudWatchLogsSender
from .s3.standerd_stream_s3_sender import StanderdStreamS3Sender


class StanderdStreamCloudWatchS3Sender(CloudWatchAndS3Parent):
    """
    CloudWatch LogsとS3の両方へ標準出力・標準エラー出力をストリーム出力するクラス
    
    StanderdStreamCloudWatchLogsSenderとStanderdStreamS3Senderの両方の機能を提供します。
    
    サブプロセスの標準出力・標準エラー出力は、CloudWatch Logs、S3、および元のsys.stdout/sys.stderrの
    すべてに同時に出力されます（tee的な動作）。
    
    ### サブプロセスの標準出力・標準エラー出力をリダイレクトする例
    
    ```python
    import subprocess
    from _tool_.lib.cloud_watch_s3_stream import StanderdStreamCloudWatchS3Sender
    
    # CloudWatch LogsとS3に出力するストリームを作成
    with StanderdStreamCloudWatchS3Sender(
        log_group_name="my-log-group",
        log_stream_name="my-log-stream",
        bucket_name="my-bucket",
        key="output/script",
        suffix=".log",
    ) as stream:
        # サブプロセスを開始し、サブプロセスの標準出力と標準エラー出力を作成したストリームにリダイレクト
        #   → サブプロセスの標準出力と標準エラー出力がCloudWatch Logs、S3、および元のsys.stdout/stderrに出力される
        process = subprocess.Popen(
            ["python", "script.py"],
            stdout=stream.stdout,
            stderr=stream.stderr,
            text=True
        )
        # サブプロセスの完了を待つ
        process.wait()
    ```
    
    ### 現在のプロセスの標準出力・標準エラー出力をリダイレクトする例
    
    ```python
    import sys
    from _tool_.lib.cloud_watch_s3_stream import StanderdStreamCloudWatchS3Sender
    
    with StanderdStreamCloudWatchS3Sender(
        log_group_name="my-log-group",
        log_stream_name="my-log-stream",
        bucket_name="my-bucket",
        key="output/script",
        suffix=".log",
    ) as stream:
        # 標準出力と標準エラー出力をリダイレクト
        sys.stdout = stream.stdout
        sys.stderr = stream.stderr
        
        print("This will be sent to CloudWatch Logs, S3, and also displayed on the console")
        print("Error message", file=sys.stderr)
    ```
    
    ## 既存リソースが見つからない場合の挙動
    
    ### CloudWatch Logs
    
    指定されたロググループまたはログストリームが存在しない場合、自動的に作成されます。
    作成に失敗した場合でも、警告メッセージを標準エラー出力に出力するだけで、プログラムの実行は継続されます。
    
    ### S3
    
    指定されたS3キー（ファイル）が存在しない場合、自動的に新規作成されます。
    マルチパートアップロードまたは通常のアップロードを使用して、データをS3に書き込みます。
    アップロードに失敗した場合は例外が発生しますが、エラーハンドリングによりアップロードは中止されます。
    
    いずれかのリソース作成・書き込みに失敗した場合でも、プログラム自体は停止しません。
    
    ## 必要なIAM権限
    
    このクラスを使用するには、以下のIAM権限が必要です：
    
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
                "Resource": "arn:aws:s3:::bucket-name/*"
            }
        ]
    }
    ```
    """
    
    def __init__(
        self,
        *,
        parent: Optional[CloudWatchAndS3Parent] = None,
        log_group_name: str = "",
        log_stream_name: str = "",
        bucket_name: str = "",
        key: str = "",
        suffix: str = ".log",
        encoding: str = "utf-8"
    ):
        """
        初期化
        
        Args:
            log_group_name: CloudWatch Logsのロググループ名
            log_stream_name: CloudWatch Logsのログストリーム名
            bucket_name: S3バケット名
            stdout_key: 標準出力のS3キー（パス）
            stderr_key: エラー出力のS3キー（パス）
            encoding: テキストエンコーディング（デフォルト: utf-8）
        """
        # 親から引き継ぎ、引数で上書き
        self._log_group_name = log_group_name or (parent.log_group_name if parent else "")
        self._log_stream_name = log_stream_name or (parent.log_stream_name if parent else "")
        self._name = parent.name if parent else ""

        self._bucket_name = bucket_name or (parent.bucket_name if parent else "")
        self._key_base = key or (parent.key if parent else "")
        self._stdout_key = f"{self._key_base}{suffix}" if self._key_base else ""
        self._stderr_key = f"{self._key_base}_ERROR{suffix}" if self._key_base else ""

        # CloudWatch Logs用のストリーム
        self._cw_stream = StanderdStreamCloudWatchLogsSender(
            log_group_name=log_group_name,
            log_stream_name=log_stream_name,
            encoding=encoding
        )
        
        # S3用ストリーム送信者（標準出力・標準エラーを内包）
        self._s3_sender = None
        if self._key_base:
            self._s3_sender = StanderdStreamS3Sender(
                bucket_name=self._bucket_name,
                key=self._key_base,
                suffix=suffix,
                encoding=encoding
            )
        
        # ストリームオブジェクト（__enter__でCombinedStreamWriterをセットし、__exit__でクローズする一時的なハンドラ）
        self.stdout = None
        self.stderr = None

    @property
    def log_group_name(self) -> str:
        return self._log_group_name

    @property
    def log_stream_name(self) -> str:
        return self._log_stream_name

    @property
    def name(self) -> str:
        return self._name

    @property
    def bucket_name(self) -> str:
        return self._bucket_name

    @property
    def key(self) -> str:
        return self._key_base
    
    def _create_combined_stream(self, is_stderr: bool):
        """
        両方のストリームに書き込むストリームオブジェクトを作成
        
        Args:
            is_stderr: 標準エラー出力かどうか
        
        Returns:
            ストリームオブジェクト
        """
        class CombinedStreamWriter:
            def __init__(self, parent, is_stderr):
                self.parent = parent
                self.is_stderr = is_stderr
                self.closed = False
                
                # パイプを作成（subprocess用）
                self.read_fd, self.write_fd = os.pipe()
                
                # 各ストリームのwriterを取得
                if is_stderr:
                    self.cw_writer = parent._cw_stream.stderr
                    self.s3_writer = parent._s3_sender.stderr_pipe if parent._s3_sender else None
                    # 元のsys.stderrを保存（標準出力にも出力するため）
                    self.original_stream = sys.stderr
                else:
                    self.cw_writer = parent._cw_stream.stdout
                    self.s3_writer = parent._s3_sender.stdout_pipe if parent._s3_sender else None
                    # 元のsys.stdoutを保存（標準出力にも出力するため）
                    self.original_stream = sys.stdout
                
                # パイプから読み取って書き込むスレッドを起動
                self.read_thread = threading.Thread(
                    target=self._read_from_pipe,
                    daemon=True
                )
                self.read_thread.start()
            
            def _read_from_pipe(self):
                """パイプから読み取って、CloudWatch Logs、S3、および元のsys.stdout/stderrに書き込む"""
                read_file = os.fdopen(self.read_fd, 'rb')
                try:
                    while True:
                        data = read_file.read(4096)
                        if not data:
                            break
                        
                        # 文字列に変換
                        text_data = data.decode('utf-8', errors='replace')
                        
                        # 元のsys.stdout/stderrに書き込み（標準出力にも表示）
                        try:
                            self.original_stream.write(text_data)
                            self.original_stream.flush()
                        except Exception:
                            # 標準出力への書き込みでエラーが出ても、他の出力は継続
                            pass
                        
                        # CloudWatch LogsとS3の両方に書き込み
                        if self.cw_writer:
                            self.cw_writer.write(text_data)
                        if self.s3_writer:
                            self.s3_writer.write(text_data)
                except (OSError, ValueError):
                    # パイプが閉じられた場合など
                    pass
                finally:
                    read_file.close()
            
            def fileno(self):
                """ファイルディスクリプタを返す（subprocess用）"""
                return self.write_fd
            
            def write(self, data):
                if self.closed:
                    raise ValueError("I/O operation on closed file")
                
                # パイプに書き込む（スレッドが読み取って処理する）
                if isinstance(data, str):
                    data = data.encode('utf-8')
                os.write(self.write_fd, data)
                
                return len(data)
            
            def flush(self):
                """バッファをフラッシュ（元のストリーム、CloudWatch Logs、S3のすべてをフラッシュ）"""
                try:
                    self.original_stream.flush()
                except Exception:
                    pass
                if self.cw_writer:
                    self.cw_writer.flush()
                if self.s3_writer:
                    self.s3_writer.flush()
            
            def close(self):
                """ストリームを閉じる"""
                if not self.closed:
                    # パイプの書き込み側を閉じる
                    os.close(self.write_fd)
                    # スレッドの終了を待つ
                    self.read_thread.join(timeout=1.0)
                    
                    if self.cw_writer:
                        self.cw_writer.close()
                    if self.s3_writer:
                        self.s3_writer.close()
                    self.closed = True
        
        return CombinedStreamWriter(self, is_stderr)
    
    def __enter__(self):
        """コンテキストマネージャーのエントリー"""
        # CloudWatch Logsストリームをエントリー（これにより内部のstdout/stderrが作成される）
        self._cw_stream.__enter__()
        
        # S3ストリーム送信者をエントリー
        if self._s3_sender:
            self._s3_sender.__enter__()
        
        # 結合されたストリームを作成（内部ストリームが作成された後）
        self.stdout = self._create_combined_stream(is_stderr=False)
        self.stderr = self._create_combined_stream(is_stderr=True)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        コンテキストマネージャーのエグジット（残りのログを送信）
        
        Args:
            exc_type: 例外の型
            exc_val: 例外の値
            exc_tb: トレースバック
        
        Returns:
            False（例外を伝播させる）
        """
        # ストリームを閉じる
        if self.stdout:
            self.stdout.close()
        if self.stderr:
            self.stderr.close()
        
        # CloudWatch Logsストリームでエグジット処理を実行
        cw_result = self._cw_stream.__exit__(exc_type, exc_val, exc_tb)
        
        # S3ストリーム送信者でエグジット処理を実行
        s3_result = False
        if self._s3_sender:
            s3_result = self._s3_sender.__exit__(exc_type, exc_val, exc_tb) or s3_result
        
        # どちらかがTrueを返した場合はTrueを返す（例外を抑制）
        return cw_result or s3_result

