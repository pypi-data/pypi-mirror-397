"""
社区文件上传 SDK

支持分片上传、断点续传、文件去重的异步上传客户端
"""
from .uploader import CommunityUploader
from .types import (
    FileInfo,
    UploadResult,
    UploadOptions,
    ListFilesParams,
    ProgressCallback,
)
from .exceptions import (
    UploadError,
    AuthError,
    NetworkError,
    AbortError,
)

__version__ = "1.0.0"
__all__ = [
    "CommunityUploader",
    "FileInfo",
    "UploadResult",
    "UploadOptions",
    "ListFilesParams",
    "ProgressCallback",
    "UploadError",
    "AuthError",
    "NetworkError",
    "AbortError",
]
