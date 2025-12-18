import boto3
import json
import uuid
import traceback
from datetime import datetime, timezone
from typing import Optional, Any
from botocore.exceptions import ClientError


class CloudWatchLogsLoggerContext:
    """
    CloudWatchLogsへログを出力するコンテキストマネージャー
    
    ```python
    with CloudWatchLogsLoggerContext(parent=None, log_group_name="test_group", log_stream_name="test_stream") as logger:
        logger.info("Hello, World!")
    ```

    ↑のような利用を前提としている。
    出力はJSON形式で、以下のような構造になる。

    ### 文字列が渡された場合
    ```json
    {
        "execution_id": "THIS_IS_UIDv7_STRING",  # @REVIEW: execution_idを追加してください。親コンテキストから引き継ぐ値を想定しており、ロググループ内で実行単位を識別するために利用する想定です。
        "timestamp": "2025-01-01T00:00:00.000Z",
        "level": "INFO",
        "name": "祖先処理名.親処理名.処理名",
        "message_obj": "Hello, World!"
    }
    ```

    ### 辞書などが渡された場合
    ```json
    {
        "execution_id": "THIS_IS_UIDv7_STRING",
        "timestamp": "2025-01-01T00:00:00.000Z",
        "level": "INFO",
        "name": "祖先処理名.親処理名.処理名",
        "message_obj": {"key": "value"}
    }
    ```

    ※message_objはjson.dumps(indent=4, ensure_ascii=False)の結果が入る。
    
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
        parent: Optional['CloudWatchLogsLoggerContext'] = None,
        log_group_name: str = "",
        log_stream_name: str = "",
        name: str = "",
        execution_id: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            parent: 親のロガーコンテキスト（階層的な名前管理のため）
            log_group_name: CloudWatch Logsのロググループ名（親がある場合は親から引き継ぎ、設定されていれば上書き）
            log_stream_name: CloudWatch Logsのログストリーム名（親がある場合は親から引き継ぎ、設定されていれば上書き）
            name: このロガーの名前（親がある場合は親の名前.この名前になる）
            execution_id: 実行ID（UIDv7形式の文字列。親がある場合は親から引き継ぐ）
        """
        self.parent = parent
        self._name = name  # このインスタンスの名前（親の名前は含まない）
        
        # execution_idを設定（親から引き継ぐ、または新規生成）
        if parent:
            self.execution_id = parent.execution_id
        elif execution_id:
            self.execution_id = execution_id
        else:
            # UUIDv7風のIDを生成（タイムスタンプベースの一意なID、Pythonのuuidはv4のみなので…）
            self.execution_id = self._generate_execution_id()
        
        self.client = boto3.client('logs')
        self.log_events = []  # バッファリング用
        
        # ロググループ名とログストリーム名を設定（親から引き継ぎ、引数で上書き可能）
        if parent:
            # 親から引き継ぎ、引数が設定されていれば上書き
            self._log_group_name = log_group_name if log_group_name else parent.log_group_name
            self._log_stream_name = log_stream_name if log_stream_name else parent.log_stream_name
        else:
            # 親がない場合は引数の値を使用
            self._log_group_name = log_group_name
            self._log_stream_name = log_stream_name
        
        # ロググループとストリームが設定されている場合のみ、存在確認と作成を行う
        if self._log_group_name and self._log_stream_name:
            self._ensure_log_group_and_stream()
    
    def _generate_execution_id(self) -> str:
        """
        実行IDを生成（UIDv7風のタイムスタンプベースのID）
        
        Returns:
            UIDv7形式の文字列
        """
        # タイムスタンプ（ミリ秒）とランダム部分を組み合わせたIDを生成
        timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        random_part = uuid.uuid4().hex[:12]
        return f"{timestamp_ms:013x}{random_part}"
    
    @property
    def log_group_name(self) -> str:
        """ロググループ名を取得"""
        return self._log_group_name
    
    @property
    def log_stream_name(self) -> str:
        """ログストリーム名を取得"""
        return self._log_stream_name
    
    @property
    def name(self) -> str:
        """階層的な名前を取得（親処理名.このインスタンスの処理名）"""
        if self.parent and self.parent.name:
            return f"{self.parent.name}.{self._name}" if self._name else self.parent.name
        return self._name
    
    def _ensure_log_group_and_stream(self):
        """ロググループとログストリームの存在確認と作成"""
        try:
            # ロググループの存在確認
            try:
                self.client.describe_log_groups(logGroupNamePrefix=self.log_group_name)
                # 存在するかチェック（完全一致）
                groups = self.client.describe_log_groups(logGroupNamePrefix=self.log_group_name)['logGroups']
                if not any(g['logGroupName'] == self.log_group_name for g in groups):
                    # ロググループが存在しない場合は作成
                    self.client.create_log_group(logGroupName=self.log_group_name)
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    self.client.create_log_group(logGroupName=self.log_group_name)
                else:
                    raise
            
            # ログストリームの存在確認
            try:
                streams = self.client.describe_log_streams(
                    logGroupName=self.log_group_name,
                    logStreamNamePrefix=self.log_stream_name
                )['logStreams']
                
                matching_stream = next(
                    (s for s in streams if s['logStreamName'] == self.log_stream_name),
                    None
                )
                
                if not matching_stream:
                    # ストリームが存在しない場合は作成
                    self.client.create_log_stream(
                        logGroupName=self.log_group_name,
                        logStreamName=self.log_stream_name
                    )
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    self.client.create_log_stream(
                        logGroupName=self.log_group_name,
                        logStreamName=self.log_stream_name
                    )
                else:
                    raise
        except Exception as e:
            # エラーが発生した場合でも処理を続行（ログ出力は失敗するが、プログラムは継続）
            print(f"Warning: Failed to setup CloudWatch Logs: {e}", file=__import__('sys').stderr)
    
    def _format_message(self, message_obj: Any) -> str:
        """
        メッセージオブジェクトをJSON形式の文字列に変換
        
        Args:
            message_obj: メッセージ（文字列、辞書、リストなど）
        
        Returns:
            JSON形式の文字列（indent=4, ensure_ascii=False）
        """
        if isinstance(message_obj, str):
            return message_obj
        else:
            return json.dumps(message_obj, indent=4, ensure_ascii=False)
    
    def _create_log_event(self, level: str, message_obj: Any) -> dict:
        """
        ログイベントを作成
        
        Args:
            level: ログレベル（INFO, WARNING, ERROR, DEBUG）
            message_obj: メッセージオブジェクト
        
        Returns:
            ログイベントの辞書
        """
        timestamp = datetime.now(timezone.utc)
        timestamp_ms = int(timestamp.timestamp() * 1000)
        
        log_data = {
            "execution_id": self.execution_id,
            "timestamp": timestamp.isoformat().replace('+00:00', 'Z'),
            "level": level,
            "name": self.name,
            "message_obj": self._format_message(message_obj)
        }
        
        return {
            "timestamp": timestamp_ms,
            "message": json.dumps(log_data, ensure_ascii=False)
        }
    
    def _send_log_events(self):
        """
        バッファリングされたログイベントをCloudWatch Logsに送信
        バッファリングは行わず、一律で送信する
        
        注意: AWS CloudWatch Logsは2023年1月以降、sequenceTokenの要件を削除しました。
        したがって、sequenceTokenの管理は不要です。
        """
        if not self.log_events:
            return
        
        try:
            self.client.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name,
                logEvents=self.log_events
            )
            self.log_events = []
        except Exception as e:
            # エラーが発生した場合でも処理を続行（ログ出力は失敗するが、プログラムは継続）
            print(f"Warning: Failed to send log to CloudWatch Logs: {e}", file=__import__('sys').stderr)
    
    def _log(self, level: str, message_obj: Any):
        """
        ログを出力
        
        Args:
            level: ログレベル
            message_obj: メッセージオブジェクト
        """
        log_event = self._create_log_event(level, message_obj)
        self.log_events.append(log_event)
        self._send_log_events()
    
    def info(self, message_obj: Any):
        """INFOレベルのログを出力"""
        self._log("INFO", message_obj)
    
    def warning(self, message_obj: Any):
        """WARNINGレベルのログを出力"""
        self._log("WARNING", message_obj)
    
    def error(self, message_obj: Any):
        """ERRORレベルのログを出力"""
        self._log("ERROR", message_obj)
    
    def debug(self, message_obj: Any):
        """DEBUGレベルのログを出力"""
        self._log("DEBUG", message_obj)
    
    def __enter__(self):
        """コンテキストマネージャーのエントリー"""
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
        # 例外が発生した場合はログに出力
        if exc_type is not None:
            error_info = {
                "exception_type": exc_type.__name__ if exc_type else None,
                "exception_message": str(exc_val) if exc_val else None,
                "traceback": traceback.format_exception(exc_type, exc_val, exc_tb) if exc_tb else None
            }
            self.error(error_info)
        
        # 残りのログを送信
        self._send_log_events()
        return False  # 例外を伝播させる
