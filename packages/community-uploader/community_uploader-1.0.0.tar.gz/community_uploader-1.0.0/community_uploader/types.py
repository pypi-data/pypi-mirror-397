"""
类型定义
"""
from dataclasses import dataclass, field
from typing import Optional, Callable, Any, Awaitable, Union
from enum import Enum


# 进度回调类型
ProgressCallback = Callable[[float], None]
AsyncProgressCallback = Callable[[float], Awaitable[None]]


class FileCategory(str, Enum):
    """文件分类"""
    GENERAL = "general"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    AVATAR = "avatar"
    COVER = "cover"


class FileStatus(str, Enum):
    """文件状态"""
    PENDING = "pending"
    UPLOADING = "uploading"
    CONFIRMED = "confirmed"
    FAILED = "failed"


@dataclass
class FileInfo:
    """文件信息"""
    id: str
    file_key: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    file_ext: Optional[str] = None
    file_md5: Optional[str] = None
    bucket: Optional[str] = None
    region: Optional[str] = None
    oss_url: Optional[str] = None
    imagekit_url: Optional[str] = None
    cdn_url: Optional[str] = None
    category: str = "general"
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    status: str = "pending"
    related_type: Optional[str] = None
    related_id: Optional[str] = None
    extra_metadata: dict = field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    confirmed_at: Optional[str] = None
    deleted_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "FileInfo":
        """从字典创建 FileInfo 对象"""
        return cls(
            id=data.get("id", ""),
            file_key=data.get("file_key", ""),
            file_size=data.get("file_size"),
            file_type=data.get("file_type"),
            file_ext=data.get("file_ext"),
            file_md5=data.get("file_md5"),
            bucket=data.get("bucket"),
            region=data.get("region"),
            oss_url=data.get("oss_url"),
            imagekit_url=data.get("imagekit_url"),
            cdn_url=data.get("cdn_url"),
            category=data.get("category", "general"),
            user_id=data.get("user_id"),
            org_id=data.get("org_id"),
            status=data.get("status", "pending"),
            related_type=data.get("related_type"),
            related_id=data.get("related_id"),
            extra_metadata=data.get("extra_metadata", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            confirmed_at=data.get("confirmed_at"),
            deleted_at=data.get("deleted_at"),
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "file_key": self.file_key,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "file_ext": self.file_ext,
            "file_md5": self.file_md5,
            "bucket": self.bucket,
            "region": self.region,
            "oss_url": self.oss_url,
            "imagekit_url": self.imagekit_url,
            "cdn_url": self.cdn_url,
            "category": self.category,
            "user_id": self.user_id,
            "org_id": self.org_id,
            "status": self.status,
            "related_type": self.related_type,
            "related_id": self.related_id,
            "extra_metadata": self.extra_metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "confirmed_at": self.confirmed_at,
            "deleted_at": self.deleted_at,
        }


@dataclass
class UploadResult:
    """上传结果"""
    file: FileInfo
    deduplicated: bool = False  # 是否命中去重（秒传）

    @classmethod
    def from_dict(cls, data: dict, deduplicated: bool = False) -> "UploadResult":
        """从字典创建"""
        return cls(
            file=FileInfo.from_dict(data),
            deduplicated=deduplicated,
        )


@dataclass
class UploadOptions:
    """上传选项"""
    category: str = "general"
    content_type: Optional[str] = None
    part_size: Optional[int] = None
    metadata: Optional[dict] = None
    on_progress: Optional[Union[ProgressCallback, AsyncProgressCallback]] = None
    on_md5_progress: Optional[Union[ProgressCallback, AsyncProgressCallback]] = None
    # API Key 认证时可指定用户信息（覆盖客户端级别的设置）
    user_id: Optional[str] = None
    org_id: Optional[str] = None


@dataclass
class ListFilesParams:
    """文件列表查询参数"""
    category: Optional[str] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20


@dataclass
class PartInfo:
    """分片信息"""
    part_number: int
    start: int
    end: int
    size: int
    upload_url: Optional[str] = None
    uploaded: bool = False
    etag: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "PartInfo":
        """从字典创建"""
        return cls(
            part_number=data.get("part_number", 0),
            start=data.get("start", 0),
            end=data.get("end", 0),
            size=data.get("size", 0),
            upload_url=data.get("upload_url"),
            uploaded=data.get("uploaded", False),
            etag=data.get("etag"),
        )
