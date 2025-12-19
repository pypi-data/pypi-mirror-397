"""
社区文件上传 SDK - 核心上传器

支持:
- 分片上传
- 断点续传
- 文件去重（秒传）
- 并发上传
- 进度回调
"""
import asyncio
import hashlib
import mimetypes
import os
from io import BytesIO
from pathlib import Path
from typing import Optional, Union, Callable, Awaitable, BinaryIO, List

import aiohttp
import aiofiles

from .types import (
    FileInfo,
    UploadResult,
    UploadOptions,
    ListFilesParams,
    PartInfo,
    ProgressCallback,
)
from .exceptions import UploadError, AuthError, NetworkError, AbortError


# Token 获取函数类型
TokenGetter = Union[Callable[[], str], Callable[[], Awaitable[str]]]
# 日志回调类型
LogCallback = Callable[[str], None]


class CommunityUploader:
    """
    社区文件上传客户端

    支持分片上传、断点续传、文件去重的异步上传客户端

    Example:
        ```python
        uploader = CommunityUploader(
            base_url="https://api.example.com",
            get_token=lambda: "your-token"
        )

        result = await uploader.upload(
            file_path="/path/to/file.mp4",
            options=UploadOptions(
                category="video",
                on_progress=lambda p: print(f"上传进度: {p:.1f}%")
            )
        )
        print(f"上传完成: {result.file.oss_url}")
        ```
    """

    # 默认分块大小（用于 MD5 计算）
    MD5_CHUNK_SIZE = 2 * 1024 * 1024  # 2MB

    # 文件类型映射
    MIME_TYPES = {
        ".mp4": "video/mp4",
        ".mov": "video/quicktime",
        ".avi": "video/x-msvideo",
        ".mkv": "video/x-matroska",
        ".webm": "video/webm",
        ".flv": "video/x-flv",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xls": "application/vnd.ms-excel",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".ppt": "application/vnd.ms-powerpoint",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".txt": "text/plain",
    }

    def __init__(
        self,
        base_url: str,
        get_token: TokenGetter = None,
        api_key: Optional[str] = None,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        concurrency: int = 3,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        timeout: float = 300.0,
        on_log: Optional[LogCallback] = None,
    ):
        """
        初始化上传客户端

        Args:
            base_url: API 基础地址
            get_token: 获取认证令牌的函数（支持同步和异步）
            api_key: API Key（用于内部服务调用，与 get_token 二选一）
            user_id: 用户ID（使用 API Key 认证时必填）
            org_id: 组织ID（使用 API Key 认证时可选）
            concurrency: 并发上传分片数（默认 3）
            retry_count: 失败重试次数（默认 3）
            retry_delay: 重试延迟秒数（默认 1.0）
            timeout: 请求超时秒数（默认 300）
            on_log: 日志回调函数
        """
        self.base_url = base_url.rstrip("/")
        self._get_token = get_token
        self._api_key = api_key
        self._user_id = user_id
        self._org_id = org_id
        self.concurrency = concurrency
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.timeout = timeout
        self._on_log = on_log
        self._session: Optional[aiohttp.ClientSession] = None
        self._cancelled = False

    def _log(self, message: str):
        """输出日志"""
        if self._on_log:
            self._on_log(message)

    async def _get_token_async(self) -> str:
        """异步获取 token"""
        result = self._get_token()
        if asyncio.iscoroutine(result):
            result = await result
        # 自动添加 Bearer 前缀
        if result and not result.startswith("Bearer "):
            result = f"Bearer {result}"
        return result

    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建 HTTP 会话"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        """关闭 HTTP 会话"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _request(
        self,
        method: str,
        path: str,
        json: dict = None,
        params: dict = None,
        headers: dict = None,
    ) -> dict:
        """发送 API 请求"""
        session = await self._get_session()

        url = f"{self.base_url}{path}"
        req_headers = {
            "Content-Type": "application/json",
        }

        # 支持两种认证方式：API Key 或 Token
        if self._api_key:
            req_headers["X-API-Key"] = self._api_key
        elif self._get_token:
            token = await self._get_token_async()
            req_headers["Authorization"] = token

        if headers:
            req_headers.update(headers)

        for attempt in range(self.retry_count):
            try:
                async with session.request(
                    method,
                    url,
                    json=json,
                    params=params,
                    headers=req_headers,
                ) as response:
                    data = await response.json()

                    if response.status == 401:
                        raise AuthError("认证失败，请检查 token", code=401)

                    if response.status >= 400:
                        error_msg = data.get("message", f"请求失败: {response.status}")
                        raise UploadError(error_msg, code=response.status, details=data)

                    # 检查业务错误码
                    if data.get("code") not in [0, 1000, None]:
                        raise UploadError(
                            data.get("message", "请求失败"),
                            code=data.get("code"),
                            details=data,
                        )

                    return data.get("data", data)

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < self.retry_count - 1:
                    delay = self.retry_delay * (attempt + 1)
                    self._log(f"请求失败，{delay}s 后重试: {e}")
                    await asyncio.sleep(delay)
                else:
                    raise NetworkError(f"网络请求失败: {e}")

    async def calculate_md5(
        self,
        file: Union[str, Path, bytes, BinaryIO],
        on_progress: Optional[ProgressCallback] = None,
    ) -> str:
        """
        计算文件 MD5

        Args:
            file: 文件路径、字节数据或文件对象
            on_progress: 进度回调 (0-100)

        Returns:
            MD5 哈希值（小写）
        """
        md5_hash = hashlib.md5()
        total_size = 0
        processed = 0

        # 获取文件大小
        if isinstance(file, (str, Path)):
            total_size = os.path.getsize(file)
        elif isinstance(file, bytes):
            total_size = len(file)
        elif hasattr(file, "seek") and hasattr(file, "read"):
            pos = file.tell()
            file.seek(0, 2)
            total_size = file.tell()
            file.seek(pos)

        async def update_progress():
            if on_progress and total_size > 0:
                percent = (processed / total_size) * 100
                if asyncio.iscoroutinefunction(on_progress):
                    await on_progress(percent)
                else:
                    on_progress(percent)

        if isinstance(file, (str, Path)):
            # 文件路径
            async with aiofiles.open(file, "rb") as f:
                while True:
                    chunk = await f.read(self.MD5_CHUNK_SIZE)
                    if not chunk:
                        break
                    md5_hash.update(chunk)
                    processed += len(chunk)
                    await update_progress()

        elif isinstance(file, bytes):
            # 字节数据
            for i in range(0, len(file), self.MD5_CHUNK_SIZE):
                chunk = file[i : i + self.MD5_CHUNK_SIZE]
                md5_hash.update(chunk)
                processed += len(chunk)
                await update_progress()

        else:
            # 文件对象
            while True:
                chunk = file.read(self.MD5_CHUNK_SIZE)
                if not chunk:
                    break
                if asyncio.iscoroutine(chunk):
                    chunk = await chunk
                md5_hash.update(chunk)
                processed += len(chunk)
                await update_progress()

        return md5_hash.hexdigest()

    def _get_file_info(
        self, file: Union[str, Path, bytes, BinaryIO], file_name: Optional[str] = None
    ) -> tuple[str, int, str, str]:
        """
        获取文件信息

        Returns:
            (文件名, 文件大小, MIME 类型, 文件扩展名)
        """
        if isinstance(file, (str, Path)):
            path = Path(file)
            name = file_name or path.name
            size = path.stat().st_size
        elif isinstance(file, bytes):
            name = file_name or "file"
            size = len(file)
        else:
            name = file_name or getattr(file, "name", "file")
            pos = file.tell()
            file.seek(0, 2)
            size = file.tell()
            file.seek(pos)

        # 获取文件扩展名和 MIME 类型
        ext = Path(name).suffix.lower().lstrip('.')
        mime_type = self.MIME_TYPES.get(f".{ext}") or mimetypes.guess_type(name)[0] or "application/octet-stream"

        return name, size, mime_type, ext

    async def upload(
        self,
        file: Union[str, Path, bytes, BinaryIO],
        file_name: Optional[str] = None,
        options: Optional[UploadOptions] = None,
    ) -> UploadResult:
        """
        上传文件

        支持自动 MD5 计算、去重、断点续传

        Args:
            file: 文件路径、字节数据或文件对象
            file_name: 文件名（可选，从文件路径自动获取）
            options: 上传选项

        Returns:
            上传结果，包含文件信息

        Raises:
            UploadError: 上传失败
            AbortError: 上传被取消
        """
        self._cancelled = False
        options = options or UploadOptions()

        # 获取文件信息
        name, size, mime_type, file_ext = self._get_file_info(file, file_name)
        content_type = options.content_type or mime_type

        self._log(f"开始上传: {name}, 扩展名: {file_ext}, 大小: {size} 字节")

        # 计算 MD5
        self._log("计算文件 MD5...")
        file_md5 = await self.calculate_md5(file, options.on_md5_progress)
        self._log(f"MD5: {file_md5}")

        if self._cancelled:
            raise AbortError()

        # 初始化上传
        self._log("初始化上传...")
        # 用户信息优先级：options > 客户端配置
        user_id = options.user_id or self._user_id
        org_id = options.org_id or self._org_id
        init_result = await self._init_upload(
            file_ext=file_ext,
            file_size=size,
            file_md5=file_md5,
            category=options.category,
            content_type=content_type,
            part_size=options.part_size,
            metadata=options.metadata,
            user_id=user_id,
            org_id=org_id,
        )

        status = init_result.get("status")

        # 去重命中，秒传
        if status == "completed":
            self._log("文件已存在，秒传成功")
            return UploadResult.from_dict(init_result.get("file", {}), deduplicated=True)

        if self._cancelled:
            raise AbortError()

        # 需要上传分片
        file_id = init_result.get("file_id")
        parts = [PartInfo.from_dict(p) for p in init_result.get("parts", [])]

        # 过滤出需要上传的分片
        pending_parts = [p for p in parts if not p.uploaded]
        total_parts = len(parts)
        uploaded_count = total_parts - len(pending_parts)

        if status == "resuming":
            self._log(f"断点续传: 已上传 {uploaded_count}/{total_parts} 个分片")
        else:
            self._log(f"新上传: 共 {total_parts} 个分片")

        # 并发上传分片
        await self._upload_parts(
            file=file,
            parts=pending_parts,
            total_parts=total_parts,
            uploaded_count=uploaded_count,
            on_progress=options.on_progress,
        )

        if self._cancelled:
            raise AbortError()

        # 完成上传
        self._log("完成上传...")
        result = await self._complete_upload(file_id)

        self._log("上传完成")
        return UploadResult.from_dict(result)

    async def _init_upload(
        self,
        file_ext: str,
        file_size: int,
        file_md5: str,
        category: str = "general",
        content_type: Optional[str] = None,
        part_size: Optional[int] = None,
        metadata: Optional[dict] = None,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> dict:
        """初始化上传"""
        payload = {
            "file_ext": file_ext,
            "file_size": file_size,
            "file_md5": file_md5,
            "category": category,
        }
        if content_type:
            payload["content_type"] = content_type
        if part_size:
            payload["part_size"] = part_size
        if metadata:
            payload["metadata"] = metadata
        # API Key 认证时传递用户信息
        if user_id:
            payload["user_id"] = user_id
        if org_id:
            payload["org_id"] = org_id

        return await self._request("POST", "/api/community/file/upload/init", json=payload)

    async def _upload_parts(
        self,
        file: Union[str, Path, bytes, BinaryIO],
        parts: List[PartInfo],
        total_parts: int,
        uploaded_count: int = 0,
        on_progress: Optional[ProgressCallback] = None,
    ):
        """并发上传分片"""
        if not parts:
            return

        session = await self._get_session()
        completed = uploaded_count
        lock = asyncio.Lock()

        async def update_progress():
            if on_progress:
                percent = (completed / total_parts) * 100
                if asyncio.iscoroutinefunction(on_progress):
                    await on_progress(percent)
                else:
                    on_progress(percent)

        async def upload_part(part: PartInfo):
            nonlocal completed

            if self._cancelled:
                return

            # 读取分片数据
            if isinstance(file, (str, Path)):
                async with aiofiles.open(file, "rb") as f:
                    await f.seek(part.start)
                    data = await f.read(part.size)
            elif isinstance(file, bytes):
                data = file[part.start : part.end]
            else:
                file.seek(part.start)
                data = file.read(part.size)
                if asyncio.iscoroutine(data):
                    data = await data

            # 上传到 OSS
            for attempt in range(self.retry_count):
                if self._cancelled:
                    return

                try:
                    # 注意：必须显式设置 skip_auto_headers 跳过自动添加的 Content-Type
                    # 否则 aiohttp 会自动添加 Content-Type: application/octet-stream
                    # 导致与 OSS 签名不匹配（SignatureDoesNotMatch 错误）
                    async with session.put(
                        part.upload_url,
                        data=data,
                        skip_auto_headers=["Content-Type"],
                    ) as response:
                        if response.status not in [200, 201]:
                            text = await response.text()
                            raise UploadError(f"分片上传失败: {response.status} - {text}")

                        # 成功
                        async with lock:
                            completed += 1
                            await update_progress()
                        return

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt < self.retry_count - 1:
                        delay = self.retry_delay * (attempt + 1)
                        self._log(f"分片 {part.part_number} 上传失败，{delay}s 后重试: {e}")
                        await asyncio.sleep(delay)
                    else:
                        raise NetworkError(f"分片 {part.part_number} 上传失败: {e}")

        # 初始进度
        await update_progress()

        # 使用信号量控制并发
        semaphore = asyncio.Semaphore(self.concurrency)

        async def upload_with_semaphore(part: PartInfo):
            async with semaphore:
                await upload_part(part)

        # 并发上传
        tasks = [upload_with_semaphore(part) for part in parts]
        await asyncio.gather(*tasks)

    async def _complete_upload(self, file_id: str) -> dict:
        """完成上传"""
        payload = {"file_id": file_id}
        # API Key 认证时需要传递 user_id
        if self._user_id:
            payload["user_id"] = self._user_id
        return await self._request(
            "POST",
            "/api/community/file/upload/complete",
            json=payload,
        )

    async def abort_upload(self, file_id: str) -> bool:
        """
        取消上传

        Args:
            file_id: 文件 ID

        Returns:
            是否取消成功
        """
        try:
            await self._request(
                "POST",
                "/api/community/file/upload/abort",
                json={"file_id": file_id},
            )
            return True
        except UploadError:
            return False

    def cancel(self):
        """取消当前上传"""
        self._cancelled = True

    async def get_file_info(self, file_id: str) -> FileInfo:
        """
        获取文件信息

        Args:
            file_id: 文件 ID

        Returns:
            文件信息
        """
        data = await self._request("GET", f"/api/community/file/{file_id}")
        return FileInfo.from_dict(data)

    async def get_file_by_url(self, url: str) -> FileInfo:
        """
        通过 URL 获取文件信息

        自动从各种 URL 格式中提取 file_key：
        - OSS URL: https://bucket.oss-accelerate.aliyuncs.com/community/videos/2025/12/xxx/file_id.mp4
        - ImageKit URL: https://ik.imagekit.io/tapnow/community/videos/2025/12/xxx/file_id.mp4
        - 直接 file_key: community/videos/2025/12/xxx/file_id.mp4

        Args:
            url: 文件 URL 或 file_key

        Returns:
            文件信息
        """
        file_key = self.extract_file_key(url)
        if not file_key:
            raise ValueError("无效的 URL 格式，无法提取 file_key")

        data = await self._request("GET", "/api/community/file/by-key", params={"file_key": file_key})
        return FileInfo.from_dict(data)

    @staticmethod
    def extract_file_key(url: str) -> Optional[str]:
        """
        从 URL 中提取 file_key

        支持：
        - OSS URL: https://bucket.oss-xxx.aliyuncs.com/path/to/file.mp4
        - ImageKit URL: https://ik.imagekit.io/tapnow/path/to/file.mp4
        - 直接 file_key: path/to/file.mp4

        Args:
            url: 文件 URL 或 file_key

        Returns:
            提取的 file_key，如果无效则返回 None
        """
        if not url:
            return None

        # 如果没有协议，认为是直接的 file_key
        if "://" not in url:
            return url.lstrip("/")

        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            hostname = parsed.hostname or ""
            pathname = parsed.path.lstrip("/")

            # OSS URL: bucket.oss-xxx.aliyuncs.com/file_key
            if "aliyuncs.com" in hostname:
                return pathname

            # ImageKit URL: ik.imagekit.io/tapnow/file_key
            if "imagekit.io" in hostname:
                # 移除第一个路径段（如 'tapnow'）
                parts = pathname.split("/")
                if len(parts) > 1:
                    return "/".join(parts[1:])
                return pathname

            # 其他 URL：直接返回路径
            return pathname
        except Exception:
            return None

    async def list_files(
        self, params: Optional[ListFilesParams] = None
    ) -> tuple[List[FileInfo], int]:
        """
        获取文件列表

        Args:
            params: 查询参数

        Returns:
            (文件列表, 总数)
        """
        params = params or ListFilesParams()
        query = {
            "page": params.page,
            "page_size": params.page_size,
        }
        if params.category:
            query["category"] = params.category
        if params.status:
            query["status"] = params.status

        data = await self._request("GET", "/api/community/file", params=query)

        files = [FileInfo.from_dict(f) for f in data.get("list", [])]
        total = data.get("pagination", {}).get("total", 0)

        return files, total

    async def delete_file(self, file_id: str) -> bool:
        """
        删除文件

        Args:
            file_id: 文件 ID

        Returns:
            是否删除成功
        """
        try:
            await self._request("DELETE", f"/api/community/file/{file_id}")
            return True
        except UploadError:
            return False
