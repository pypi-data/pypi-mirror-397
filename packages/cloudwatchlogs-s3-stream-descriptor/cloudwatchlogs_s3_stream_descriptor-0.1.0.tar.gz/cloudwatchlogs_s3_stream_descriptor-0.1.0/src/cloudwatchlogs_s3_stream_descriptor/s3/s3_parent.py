from abc import ABC, abstractmethod


class S3Parent(ABC):
    """
    S3の親コンテキストを表すインターフェース
    
    このインターフェースを実装するクラスは、S3の設定情報を提供します。
    """
    
    @property
    @abstractmethod
    def bucket_name(self) -> str:
        """
        S3バケット名を取得
        
        Returns:
            S3バケット名
        """
        pass
    
    @property
    @abstractmethod
    def key(self) -> str:
        """
        S3キー（パス）を取得
        
        Returns:
            S3キー（パス）
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        階層的な名前を取得
        
        Returns:
            階層的な名前
        """
        pass

