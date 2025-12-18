from abc import ABC, abstractmethod


class CloudWatchParent(ABC):
    """
    CloudWatch Logsの親コンテキストを表すインターフェース
    
    このインターフェースを実装するクラスは、CloudWatch Logsの設定情報を提供します。
    """
    
    @property
    @abstractmethod
    def log_group_name(self) -> str:
        """
        CloudWatch Logsのロググループ名を取得
        
        Returns:
            CloudWatch Logsのロググループ名
        """
        pass
    
    @property
    @abstractmethod
    def log_stream_name(self) -> str:
        """
        CloudWatch Logsのログストリーム名を取得
        
        Returns:
            CloudWatch Logsのログストリーム名
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        階層的な名前を取得
        
        Returns:
            階層的な名前（例: "祖先処理名.親処理名.処理名"）
        """
        pass

