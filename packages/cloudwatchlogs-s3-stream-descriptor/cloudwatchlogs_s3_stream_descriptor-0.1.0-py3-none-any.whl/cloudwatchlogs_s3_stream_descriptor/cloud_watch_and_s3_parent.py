from .cloud_watch.cloud_watch_parent import CloudWatchParent
from .s3.s3_parent import S3Parent


class CloudWatchAndS3Parent(CloudWatchParent, S3Parent):
    """
    CloudWatch Logs と S3 の両方の設定を提供する親コンテキスト用インターフェース
    """
    pass

