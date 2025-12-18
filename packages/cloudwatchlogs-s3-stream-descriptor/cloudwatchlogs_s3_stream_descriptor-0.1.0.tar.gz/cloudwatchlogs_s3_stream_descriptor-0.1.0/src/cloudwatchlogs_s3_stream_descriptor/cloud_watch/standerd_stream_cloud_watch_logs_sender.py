#
# 標準出力・エラー出力をCloudWatch Logsにストリーム出力するクラス
#

from .cloud_watch_logs_stream import CloudWatchLogsStream


class StanderdStreamCloudWatchLogsSender:
    """
    CloudWatch Logsへ標準出力・標準エラー出力をストリーム出力するクラス
    
    標準出力とエラー出力をCloudWatch Logsにリアルタイムで出力します。
    
    ```python
    import subprocess
    
    with StanderdStreamCloudWatchLogsSender(
        log_group_name="my-log-group",
        log_stream_name="my-log-stream"
    ) as stream:
        # 標準出力と標準エラー出力をリダイレクト
        sys.stdout = stream.stdout
        sys.stderr = stream.stderr
        
        print("This will be sent to CloudWatch Logs")
        print("Error message", file=sys.stderr)
    ```
    
    ## 既存リソースが見つからない場合の挙動
    
    指定されたロググループまたはログストリームが存在しない場合、自動的に作成されます。
    作成に失敗した場合でも、警告メッセージを標準エラー出力に出力するだけで、プログラムの実行は継続されます。
    この場合、ログ出力は失敗しますが、プログラム自体は停止しません。
    
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
            }
        ]
    }
    ```
    """
    
    def __init__(
        self,
        *,
        log_group_name: str,
        log_stream_name: str,
        encoding: str = "utf-8"
    ):
        """
        初期化
        
        Args:
            log_group_name: CloudWatch Logsのロググループ名
            log_stream_name: CloudWatch Logsのログストリーム名
            encoding: テキストエンコーディング（デフォルト: utf-8）
        """
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        self.encoding = encoding
        
        # 標準出力用とエラー出力用のCloudWatchLogsStreamを作成
        self._stdout_stream = None
        self._stderr_stream = None
        
        # ストリームオブジェクト（__enter__でセットし、__exit__でクローズする一時的なハンドラ）
        self.stdout = None
        self.stderr = None
    
    def __enter__(self):
        """コンテキストマネージャーのエントリー"""
        # 標準出力用のCloudWatchLogsStreamを作成
        self._stdout_stream = CloudWatchLogsStream(
            log_group_name=self.log_group_name,
            log_stream_name=self.log_stream_name,
            encoding=self.encoding
        )
        self._stdout_stream.__enter__()
        
        # エラー出力用のCloudWatchLogsStreamを作成
        self._stderr_stream = CloudWatchLogsStream(
            log_group_name=self.log_group_name,
            log_stream_name=self.log_stream_name,
            encoding=self.encoding
        )
        self._stderr_stream.__enter__()
        
        # ストリームオブジェクトを設定
        self.stdout = self._stdout_stream.pipe
        self.stderr = self._stderr_stream.pipe
        
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
        # 標準出力のストリームを終了
        if self._stdout_stream:
            self._stdout_stream.__exit__(exc_type, exc_val, exc_tb)
        
        # エラー出力のストリームを終了
        if self._stderr_stream:
            self._stderr_stream.__exit__(exc_type, exc_val, exc_tb)
        
        return False  # 例外を伝播させる

