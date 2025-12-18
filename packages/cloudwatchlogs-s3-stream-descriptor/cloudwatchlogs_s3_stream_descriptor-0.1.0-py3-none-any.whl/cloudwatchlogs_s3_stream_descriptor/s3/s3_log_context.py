import boto3
import json
import sys
import uuid
import traceback
from datetime import datetime, timezone
from typing import Optional, Any
from botocore.exceptions import ClientError

from .s3_parent import S3Parent


class S3LogContext:
    """
    S3へログを出力するコンテキストマネージャー
    
    CloudWatchLogsLoggerContextと同様のインターフェースで、S3にログを出力します。
    """
    
    def __init__(
        self,
        *,
        parent: Optional[S3Parent] = None,
        bucket_name: str = "",
        key: str = "",
        name: str = "",
        execution_id: Optional[str] = None
    ):
        """
        初期化
        """
        self.parent = parent
        self._name = name  # このインスタンスの名前（親の名前は含まない）
        
        # execution_idを設定（親から引き継ぐ、または新規生成）
        if parent:
            self.execution_id = parent.execution_id
        elif execution_id:
            self.execution_id = execution_id
        else:
            self.execution_id = self._generate_execution_id()
        
        self.s3_client = boto3.client('s3')
        
        # 既存ログ内容のキャッシュ（S3からの都度取得を避ける）
        self._existing = None
        
        # バケット名とキーを設定（親から引き継ぎ、引数で上書き可能）
        if parent:
            self._bucket_name = bucket_name if bucket_name else parent.bucket_name
            self._key = key if key else parent.key
        else:
            self._bucket_name = bucket_name
            self._key = key
    
    def _generate_execution_id(self) -> str:
        """実行IDを生成（UIDv7風のタイムスタンプベースのID）"""
        timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        random_part = uuid.uuid4().hex[:12]
        return f"{timestamp_ms:013x}{random_part}"
    
    @property
    def bucket_name(self) -> str:
        """バケット名を取得"""
        return self._bucket_name
    
    @property
    def key(self) -> str:
        """S3キーを取得"""
        return self._key
    
    @property
    def name(self) -> str:
        """階層的な名前を取得（親処理名.このインスタンスの処理名）"""
        if self.parent and self.parent.name:
            return f"{self.parent.name}.{self._name}" if self._name else self.parent.name
        return self._name
    
    def _format_message(self, message_obj: Any) -> str:
        """メッセージオブジェクトをJSON形式の文字列に変換"""
        if isinstance(message_obj, str):
            return message_obj
        else:
            return json.dumps(message_obj, indent=4, ensure_ascii=False)
    
    def _create_log_entry(self, level: str, message_obj: Any) -> dict:
        """ログエントリを作成"""
        timestamp = datetime.now(timezone.utc)
        
        log_data = {
            "execution_id": self.execution_id,
            "timestamp": timestamp.isoformat().replace('+00:00', 'Z'),
            "level": level,
            "name": self.name,
            "message_obj": self._format_message(message_obj)
        }
        
        return log_data
    
    def _write_logs_to_s3(self, logs: list):
        """ログをS3に書き込み"""
        if not logs or not self._key:
            return
        
        try:
            log_lines = [json.dumps(log, ensure_ascii=False) for log in logs]
            new_log_content = '\n'.join(log_lines) + '\n'
            
            existing_content = self._existing

            # 初回のみS3から取得しキャッシュ、それ以降はキャッシュ利用
            if existing_content is None:
                try:
                    existing_content = self.s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=self._key
                    )['Body'].read().decode('utf-8')
                except ClientError as e:
                    if e.response['Error']['Code'] == 'NoSuchKey':
                        existing_content = ""
                    else:
                        raise

            log_content = (existing_content or "") + new_log_content

            # キャッシュを更新
            self._existing = log_content
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=self._key,
                Body=log_content.encode('utf-8')
            )
        except Exception as e:
            print(f"Warning: Failed to write log to S3: {e}", file=sys.stderr)
    
    def _log(self, level: str, message_obj: Any):
        """ログを出力"""
        log_entry = self._create_log_entry(level, message_obj)
        self._write_logs_to_s3([log_entry])
    
    def info(self, message_obj: Any):
        self._log("INFO", message_obj)
    
    def warning(self, message_obj: Any):
        self._log("WARNING", message_obj)
    
    def error(self, message_obj: Any):
        self._log("ERROR", message_obj)
    
    def debug(self, message_obj: Any):
        self._log("DEBUG", message_obj)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            error_info = {
                "exception_type": exc_type.__name__ if exc_type else None,
                "exception_message": str(exc_val) if exc_val else None,
                "traceback": traceback.format_exception(exc_type, exc_val, exc_tb) if exc_tb else None
            }
            self.error(error_info)
        
        return False  # 例外を伝播させる

