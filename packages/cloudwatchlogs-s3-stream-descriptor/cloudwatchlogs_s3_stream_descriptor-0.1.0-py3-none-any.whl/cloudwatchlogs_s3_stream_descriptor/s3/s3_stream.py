#
# S3へのストリーム出力を行うクラス（1つのキー用）
#

import boto3
import io
import threading
from typing import Optional
from botocore.exceptions import ClientError

from .s3_parent import S3Parent


class S3Stream(S3Parent):
    """
    S3へのストリーム出力を行うクラス（1つのキー用）
    
    1つのS3キーに対するストリーム出力を行います。
    マルチパートアップロードを使用して、リアルタイムでデータをS3に書き込みます。
    """
    
    # マルチパートアップロードの最小パートサイズ（5MB）
    MIN_PART_SIZE = 5 * 1024 * 1024
    
    def __init__(
        self,
        *,
        bucket_name: str,
        key: str,
        buffer_size: int = MIN_PART_SIZE,
        encoding: str = "utf-8"
    ):
        """
        初期化
        
        Args:
            bucket_name: S3バケット名
            key: S3キー（パス）
            buffer_size: バッファサイズ（バイト）。このサイズに達するとS3にアップロードされます
            encoding: テキストエンコーディング（デフォルト: utf-8）
        """
        self._bucket_name = bucket_name
        self._key = key
        self.buffer_size = max(buffer_size, self.MIN_PART_SIZE)
        self.encoding = encoding
        
        self.s3_client = boto3.client('s3')
        
        # バッファとアップロード管理
        self._buffer = io.BytesIO()
        self._upload_id = None
        self._part_number = 1
        self._parts = []
        self._lock = threading.Lock()
        
        # パイプ（サブプロセスに渡す用）
        self.pipe = None
    
    @property
    def bucket_name(self) -> str:
        """S3バケット名を取得"""
        return self._bucket_name
    
    @property
    def key(self) -> str:
        """S3キー（パス）を取得"""
        return self._key
    
    @property
    def name(self) -> str:
        """階層的な名前を取得"""
        return ""  # ストリーム出力用のクラスなので、名前は空文字列
    
    def _init_multipart_upload(self) -> str:
        """
        マルチパートアップロードを開始
        
        Returns:
            アップロードID
        """
        try:
            response = self.s3_client.create_multipart_upload(
                Bucket=self.bucket_name,
                Key=self.key
            )
            return response['UploadId']
        except ClientError as e:
            raise RuntimeError(f"Failed to create multipart upload for {self.key}: {e}")
    
    def _upload_part(self, upload_id: str, part_number: int, data: bytes) -> dict:
        """
        パートをアップロード
        
        Args:
            upload_id: アップロードID
            part_number: パート番号
            data: アップロードするデータ
            
        Returns:
            パート情報（ETagとPartNumberを含む辞書）
        """
        try:
            response = self.s3_client.upload_part(
                Bucket=self.bucket_name,
                Key=self.key,
                UploadId=upload_id,
                PartNumber=part_number,
                Body=data
            )
            return {
                'ETag': response['ETag'],
                'PartNumber': part_number
            }
        except ClientError as e:
            # エラー時はアップロードを中止
            try:
                self.s3_client.abort_multipart_upload(
                    Bucket=self.bucket_name,
                    Key=self.key,
                    UploadId=upload_id
                )
            except:
                pass
            raise RuntimeError(f"Failed to upload part {part_number} for {self.key}: {e}")
    
    def _complete_multipart_upload(self, upload_id: str, parts: list):
        """
        マルチパートアップロードを完了
        
        Args:
            upload_id: アップロードID
            parts: パート情報のリスト
        """
        try:
            self.s3_client.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=self.key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
        except ClientError as e:
            # エラー時はアップロードを中止
            try:
                self.s3_client.abort_multipart_upload(
                    Bucket=self.bucket_name,
                    Key=self.key,
                    UploadId=upload_id
                )
            except:
                pass
            raise RuntimeError(f"Failed to complete multipart upload for {self.key}: {e}")
    
    def _write_to_stream(self, data: bytes):
        """
        ストリームにデータを書き込み、必要に応じてS3にアップロード
        
        Args:
            data: 書き込むデータ
        """
        with self._lock:
            # バッファにデータを追加
            self._buffer.seek(0, io.SEEK_END)
            self._buffer.write(data)
            buffer_size = self._buffer.tell()
            self._buffer.seek(0)
            
            # バッファサイズが閾値を超えた場合、S3にアップロード
            while buffer_size >= self.buffer_size:
                part_data = self._buffer.read(self.buffer_size)
                
                # マルチパートアップロードを開始（まだ開始していない場合）
                if not self._upload_id:
                    self._upload_id = self._init_multipart_upload()
                
                # パートをアップロード
                part_info = self._upload_part(
                    self._upload_id,
                    self._part_number,
                    part_data
                )
                self._parts.append(part_info)
                self._part_number += 1
                
                # バッファの残りを取得
                remaining = self._buffer.read()
                self._buffer.seek(0)
                self._buffer.truncate(0)
                self._buffer.write(remaining)
                buffer_size = len(remaining)
    
    def _flush_buffer(self):
        """
        バッファの残りのデータをS3にアップロード
        """
        with self._lock:
            self._buffer.seek(0)
            remaining_data = self._buffer.read()
            self._buffer.seek(0)
            self._buffer.truncate(0)
            
            if not remaining_data:
                # データがない場合、マルチパートアップロードを完了または中止
                if self._upload_id:
                    if self._parts:
                        self._complete_multipart_upload(self._upload_id, self._parts)
                    else:
                        # パートがない場合はアップロードを中止
                        try:
                            self.s3_client.abort_multipart_upload(
                                Bucket=self.bucket_name,
                                Key=self.key,
                                UploadId=self._upload_id
                            )
                        except:
                            pass
                    self._upload_id = None
                return
            
            # マルチパートアップロードを開始（まだ開始していない場合）
            if not self._upload_id:
                # データが小さい場合は通常のアップロードを使用
                if len(remaining_data) < self.MIN_PART_SIZE:
                    try:
                        self.s3_client.put_object(
                            Bucket=self.bucket_name,
                            Key=self.key,
                            Body=remaining_data
                        )
                    except ClientError as e:
                        raise RuntimeError(f"Failed to upload to {self.key}: {e}")
                    return
                else:
                    self._upload_id = self._init_multipart_upload()
            
            # 最後のパートをアップロード
            part_info = self._upload_part(
                self._upload_id,
                len(self._parts) + 1,
                remaining_data
            )
            self._parts.append(part_info)
            
            # マルチパートアップロードを完了
            self._complete_multipart_upload(self._upload_id, self._parts)
            self._upload_id = None
    
    def _create_pipe(self):
        """
        サブプロセス用のパイプを作成
        
        Returns:
            パイプオブジェクト
        """
        class StreamPipe:
            def __init__(self, stream):
                self.stream = stream
                self.closed = False
            
            def write(self, data):
                if self.closed:
                    raise ValueError("I/O operation on closed file")
                if isinstance(data, str):
                    data = data.encode(self.stream.encoding)
                self.stream._write_to_stream(data)
                return len(data)
            
            def flush(self):
                """バッファをフラッシュ（即座にS3にアップロード）"""
                self.stream._flush_buffer()
            
            def close(self):
                self.closed = True
        
        return StreamPipe(self)
    
    def __enter__(self):
        """コンテキストマネージャーのエントリー"""
        self.pipe = self._create_pipe()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        コンテキストマネージャーのエグジット（残りのデータをアップロード）
        
        Args:
            exc_type: 例外の型
            exc_val: 例外の値
            exc_tb: トレースバック
            
        Returns:
            False（例外を伝播させる）
        """
        if self.pipe:
            self.pipe.close()
        self._flush_buffer()
        return False  # 例外を伝播させる
