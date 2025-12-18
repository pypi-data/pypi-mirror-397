from typing import Optional, Any

from .cloud_watch_and_s3_parent import CloudWatchAndS3Parent
from .cloud_watch.cloud_watch_logs_logger import CloudWatchLogsLoggerContext
from .s3.s3_log_context import S3LogContext


class CloudWatchS3LogsContext(CloudWatchAndS3Parent):
    """
    CloudWatch LogsとS3の両方へログを出力するコンテキストマネージャー
    
    CloudWatchLogsLoggerContextとS3LogContextの両方の機能を提供します。
    
    ```python
    with CloudWatchS3LogsContext(
        parent=None,
        log_group_name="my-log-group",
        log_stream_name="my-log-stream",
        bucket_name="my-bucket",
        key="logs/process",
        name="my_process"
    ) as logger:
        logger.info("Hello, World!")
    ```
    
    出力はJSON形式で、CloudWatchLogsLoggerContextと同じ構造になります。
    
    ## 既存リソースが見つからない場合の挙動
    
    ### CloudWatch Logs
    
    指定されたロググループまたはログストリームが存在しない場合、自動的に作成されます。
    作成に失敗した場合でも、警告メッセージを標準エラー出力に出力するだけで、プログラムの実行は継続されます。
    
    ### S3
    
    指定されたS3キー（ファイル）が存在しない場合、自動的に新規作成されます。
    既存のファイルがある場合は、その内容に新しいログを追記します。
    書き込みに失敗した場合でも、警告メッセージを標準エラー出力に出力するだけで、プログラムの実行は継続されます。
    
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
                    "s3:PutObject"
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
        name: str = "",
        execution_id: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            parent: 親のロガーコンテキスト（階層的な名前管理のため）
            log_group_name: CloudWatch Logsのロググループ名（親がある場合は親から引き継ぎ、設定されていれば上書き）
            log_stream_name: CloudWatch Logsのログストリーム名（親がある場合は親から引き継ぎ、設定されていれば上書き）
            bucket_name: S3バケット名（親がある場合は親から引き継ぎ、設定されていれば上書き）
            key: S3キー（親がある場合は親から引き継ぎ、設定されていれば上書き）
            name: このロガーの名前（親がある場合は親の名前.この名前になる）
            execution_id: 実行ID（UIDv7形式の文字列。親がある場合は親から引き継ぐ）
        """
        # 親インターフェースから値を引き継ぎ、引数で上書き
        resolved_log_group = log_group_name or (parent.log_group_name if parent else "")
        resolved_log_stream = log_stream_name or (parent.log_stream_name if parent else "")
        resolved_name = name or (parent.name if parent else "")

        resolved_bucket = bucket_name or (parent.bucket_name if parent else "")
        resolved_key = key or (parent.key if parent else "")
        
        # CloudWatch Logs用のロガー
        self._cw_logger = CloudWatchLogsLoggerContext(
            parent=None,
            log_group_name=resolved_log_group,
            log_stream_name=resolved_log_stream,
            name=resolved_name,
            execution_id=execution_id
        )
        
        # S3用のロガー
        self._s3_logger = S3LogContext(
            parent=None,
            bucket_name=resolved_bucket,
            key=resolved_key,
            name=resolved_name,
            execution_id=execution_id
        )
        
        self.parent = parent
    
    @property
    def execution_id(self) -> str:
        """実行IDを取得"""
        return self._cw_logger.execution_id
    
    @property
    def name(self) -> str:
        """階層的な名前を取得"""
        return self._cw_logger.name
    
    @property
    def log_group_name(self) -> str:
        """ロググループ名を取得"""
        return self._cw_logger.log_group_name
    
    @property
    def log_stream_name(self) -> str:
        """ログストリーム名を取得"""
        return self._cw_logger.log_stream_name
    
    @property
    def bucket_name(self) -> str:
        """S3バケット名を取得"""
        return self._s3_logger.bucket_name
    
    @property
    def key(self) -> str:
        """S3キーを取得"""
        return self._s3_logger.key

    # --- ログ出力系メソッド ---

    def _print_stdout(self, level: str, message_obj: Any):
        """
        標準出力にもログを出力するための内部メソッド。
        
        CloudWatch / S3 に送っている内容と同じ message_obj を
        シンプルに print する。レベルとロガー名をプレフィックスに付与する。
        """
        try:
            print(f"[{level}] {self.name}: {message_obj}")
        except Exception:
            # 標準出力への出力で例外が出ても、本来のログ送信は継続させたいので握りつぶす
            pass
    
    def info(self, message_obj: Any):
        """INFOレベルのログを出力（CloudWatch LogsとS3の両方に送信）"""
        self._cw_logger.info(message_obj)
        self._s3_logger.info(message_obj)
        self._print_stdout("INFO", message_obj)
    
    def warning(self, message_obj: Any):
        """WARNINGレベルのログを出力（CloudWatch LogsとS3の両方に送信）"""
        self._cw_logger.warning(message_obj)
        self._s3_logger.warning(message_obj)
        self._print_stdout("WARNING", message_obj)
    
    def error(self, message_obj: Any):
        """ERRORレベルのログを出力（CloudWatch LogsとS3の両方に送信）"""
        self._cw_logger.error(message_obj)
        self._s3_logger.error(message_obj)
        self._print_stdout("ERROR", message_obj)
    
    def debug(self, message_obj: Any):
        """DEBUGレベルのログを出力（CloudWatch LogsとS3の両方に送信）"""
        self._cw_logger.debug(message_obj)
        self._s3_logger.debug(message_obj)
        self._print_stdout("DEBUG", message_obj)
    
    def __enter__(self):
        """コンテキストマネージャーのエントリー"""
        self._cw_logger.__enter__()
        self._s3_logger.__enter__()
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
        # 両方のロガーでエグジット処理を実行
        cw_result = self._cw_logger.__exit__(exc_type, exc_val, exc_tb)
        s3_result = self._s3_logger.__exit__(exc_type, exc_val, exc_tb)
        
        # どちらかがTrueを返した場合はTrueを返す（例外を抑制）
        return cw_result or s3_result

