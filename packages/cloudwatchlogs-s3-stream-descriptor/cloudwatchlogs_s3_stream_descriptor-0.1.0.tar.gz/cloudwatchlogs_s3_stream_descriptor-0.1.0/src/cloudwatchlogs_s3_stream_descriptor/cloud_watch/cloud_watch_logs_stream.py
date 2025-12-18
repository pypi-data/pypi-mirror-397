#
# CloudWatch Logsへのストリーム出力を行うクラス（1つのログストリーム用）
#

import boto3
import sys
import threading
from datetime import datetime, timezone
from botocore.exceptions import ClientError


class CloudWatchLogsStream:
    """
    CloudWatch Logsへのストリーム出力を行うクラス（1つのログストリーム用）
    
    1つのログストリームに対するストリーム出力を行います。
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
        
        # boto3クライアントにタイムアウト設定を追加
        from botocore.config import Config
        config = Config(
            connect_timeout=5,
            read_timeout=5,
            retries={'max_attempts': 1}
        )
        self.client = boto3.client('logs', config=config)
        self._log_events = []
        # RLockで再入可能にし、write内での_send_log_events呼び出しによるデッドロックを防ぐ
        self._lock = threading.RLock()
        
        # パイプ（サブプロセスに渡す用）
        self.pipe = None
        
        # ロググループとストリームの存在確認と作成
        self._ensure_log_group_and_stream()
    
    def _ensure_log_group_and_stream(self):
        """ロググループとログストリームの存在確認と作成"""
        try:
            # ロググループの存在確認
            try:
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
            print(f"Warning: Failed to setup CloudWatch Logs: {e}", file=sys.stderr)
    
    def _send_log_events(self):
        """
        バッファリングされたログイベントをCloudWatch Logsに送信
        """
        if not self._log_events:
            return
        
        with self._lock:
            if not self._log_events:
                return
            
            try:
                self.client.put_log_events(
                    logGroupName=self.log_group_name,
                    logStreamName=self.log_stream_name,
                    logEvents=self._log_events.copy()
                )
                self._log_events.clear()
            except Exception as e:
                # エラーが発生した場合でも処理を続行（ログ出力は失敗するが、プログラムは継続）
                print(f"Warning: Failed to send log to CloudWatch Logs: {e}", file=sys.stderr)
    
    def _create_pipe(self):
        """
        サブプロセス用のパイプを作成
        
        Returns:
            パイプオブジェクト
        """
        class CloudWatchLogsStreamPipe:
            def __init__(self, stream):
                self.stream = stream
                self.closed = False
            
            def write(self, data):
                if self.closed:
                    raise ValueError("I/O operation on closed file")
                
                if isinstance(data, str):
                    data = data.encode(self.stream.encoding)
                
                # データを行ごとに分割
                lines = data.decode(self.stream.encoding).splitlines(keepends=True)
                
                with self.stream._lock:
                    timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
                    for line in lines:
                        # 改行文字を除去（CloudWatch Logsは改行を含めない）
                        line = line.rstrip('\n\r')
                        if line:  # 空行はスキップ
                            log_event = {
                                "timestamp": timestamp_ms,
                                "message": line
                            }
                            self.stream._log_events.append(log_event)
                            # 1行ごとに即座に送信（リアルタイム性を確保）
                            self.stream._send_log_events()
                
                return len(data)
            
            def flush(self):
                """バッファをフラッシュ（即座にCloudWatch Logsに送信）"""
                self.stream._send_log_events()
            
            def close(self):
                """ストリームを閉じる（残りのログを送信）"""
                if not self.closed:
                    self.flush()
                    self.closed = True
        
        return CloudWatchLogsStreamPipe(self)
    
    def __enter__(self):
        """コンテキストマネージャーのエントリー"""
        self.pipe = self._create_pipe()
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
        if self.pipe:
            self.pipe.close()
        
        return False  # 例外を伝播させる
