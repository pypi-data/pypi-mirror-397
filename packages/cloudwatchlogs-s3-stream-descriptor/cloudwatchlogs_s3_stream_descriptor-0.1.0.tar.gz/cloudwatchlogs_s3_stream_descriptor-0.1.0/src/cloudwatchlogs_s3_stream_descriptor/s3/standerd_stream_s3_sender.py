#
# 標準出力・エラー出力をS3にストリーム出力するクラス
#

from .s3_parent import S3Parent
from .s3_stream import S3Stream


class StanderdStreamS3Sender(S3Parent):
    """
    S3へのストリーム出力を行うクラス
    
    サブプロセスの標準出力とエラー出力をS3上のファイルにストリーム出力します。
    マルチパートアップロードを使用して、リアルタイムでデータをS3に書き込みます。
    
    指定された`key`と`suffix`から、標準出力は`{key}{suffix}`、エラー出力は`{key}_ERROR{suffix}`として自動的にS3キーが生成されます。
    `suffix`のデフォルト値は`.log`です。
    
    ```python
    import subprocess
    
    with StanderdStreamS3Sender(
        bucket_name="my-bucket",
        key="output/script"
    ) as writer:
        process = subprocess.Popen(
            ["python", "script.py"],
            stdout=writer.stdout_pipe,
            stderr=writer.stderr_pipe,
            text=True
        )
        process.wait()
    ```
    
    上記の例では、標準出力は`output/script.log`、エラー出力は`output/script_ERROR.log`としてS3に保存されます。
    
    拡張子を変更する場合は、`suffix`引数を指定します：
    
    ```python
    with StanderdStreamS3Sender(
        bucket_name="my-bucket",
        key="output/script",
        suffix=".txt"
    ) as writer:
        ...
    ```
    
    この場合、標準出力は`output/script.txt`、エラー出力は`output/script_ERROR.txt`として保存されます。
    
    ## 既存リソースが見つからない場合の挙動
    
    指定されたS3キー（ファイル）が存在しない場合、自動的に新規作成されます。
    マルチパートアップロードまたは通常のアップロードを使用して、データをS3に書き込みます。
    アップロードに失敗した場合は例外が発生しますが、エラーハンドリングによりアップロードは中止されます。
    
    ## 必要なIAM権限
    
    このクラスを使用するには、以下のIAM権限が必要です：
    
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
    """
    
    def __init__(
        self,
        *,
        bucket_name: str,
        key: str,
        suffix: str = ".log",
        buffer_size: int = S3Stream.MIN_PART_SIZE,
        encoding: str = "utf-8"
    ):
        """
        初期化
        
        Args:
            bucket_name: S3バケット名
            key: S3キーのベース（パス）
            suffix: ファイル拡張子（デフォルト: `.log`）。標準出力は`{key}{suffix}`、エラー出力は`{key}_ERROR{suffix}`として自動生成されます
            buffer_size: バッファサイズ（バイト）。このサイズに達するとS3にアップロードされます
            encoding: テキストエンコーディング（デフォルト: utf-8）
        """
        self._bucket_name = bucket_name
        self._key = key
        self.suffix = suffix
        self.buffer_size = buffer_size
        self.encoding = encoding
        
        # 標準出力用とエラー出力用のS3キーを自動生成
        self.stdout_key = f"{key}{suffix}"
        self.stderr_key = f"{key}_ERROR{suffix}"
        
        # 標準出力用とエラー出力用のS3Streamを作成
        self._stdout_stream = None
        self._stderr_stream = None
    
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
    
    @property
    def stdout_pipe(self):
        """標準出力用のパイプを取得"""
        return self._stdout_stream.pipe if self._stdout_stream else None
    
    @property
    def stderr_pipe(self):
        """エラー出力用のパイプを取得"""
        return self._stderr_stream.pipe if self._stderr_stream else None
    
    def __enter__(self):
        """コンテキストマネージャーのエントリー"""
        # 標準出力用のS3Streamを作成
        self._stdout_stream = S3Stream(
            bucket_name=self._bucket_name,
            key=self.stdout_key,
            buffer_size=self.buffer_size,
            encoding=self.encoding
        )
        self._stdout_stream.__enter__()
        
        # エラー出力用のS3Streamを作成
        self._stderr_stream = S3Stream(
            bucket_name=self._bucket_name,
            key=self.stderr_key,
            buffer_size=self.buffer_size,
            encoding=self.encoding
        )
        self._stderr_stream.__enter__()
        
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
        # 標準出力のストリームを終了
        if self._stdout_stream:
            self._stdout_stream.__exit__(exc_type, exc_val, exc_tb)
        
        # エラー出力のストリームを終了
        if self._stderr_stream:
            self._stderr_stream.__exit__(exc_type, exc_val, exc_tb)
        
        return False  # 例外を伝播させる

