# Community Uploader Python SDK

社区文件上传 SDK - 支持分片上传、断点续传、文件去重的异步上传客户端

## 特性

- **分片上传**: 自动将大文件分片上传，支持超大文件
- **断点续传**: 上传中断后可从断点继续，无需重新上传
- **文件去重**: 基于 MD5 的文件去重，相同文件秒传
- **并发上传**: 多分片并发上传，提升上传速度
- **进度追踪**: 支持 MD5 计算和上传进度回调
- **完全异步**: 基于 asyncio，支持高并发场景

## 安装

```bash
pip install community-uploader
```

或者从源码安装：

```bash
cd packages/community-uploader-python
pip install -e .
```

## 快速开始

```python
import asyncio
from community_uploader import CommunityUploader, UploadOptions

async def main():
    # 创建上传客户端
    uploader = CommunityUploader(
        base_url="https://api.example.com",
        get_token=lambda: "your-auth-token"
    )

    async with uploader:
        # 上传文件
        result = await uploader.upload(
            file="/path/to/video.mp4",
            options=UploadOptions(
                category="video",
                on_progress=lambda p: print(f"上传进度: {p:.1f}%"),
                on_md5_progress=lambda p: print(f"MD5 计算: {p:.1f}%")
            )
        )

        if result.deduplicated:
            print("文件秒传成功！")
        else:
            print(f"上传完成: {result.file.oss_url}")

asyncio.run(main())
```

## API 参考

### CommunityUploader

#### 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `base_url` | `str` | 必填 | API 基础地址 |
| `get_token` | `Callable` | 必填 | 获取认证令牌的函数（支持同步/异步） |
| `concurrency` | `int` | 3 | 并发上传分片数 |
| `retry_count` | `int` | 3 | 失败重试次数 |
| `retry_delay` | `float` | 1.0 | 重试延迟（秒） |
| `timeout` | `float` | 300.0 | 请求超时（秒） |
| `on_log` | `Callable` | None | 日志回调函数 |

#### 方法

##### `upload(file, file_name=None, options=None) -> UploadResult`

上传文件，支持自动 MD5 计算、去重、断点续传。

**参数:**
- `file`: 文件路径（str/Path）、字节数据（bytes）或文件对象
- `file_name`: 文件名（可选，从文件路径自动获取）
- `options`: 上传选项（UploadOptions）

**返回:** `UploadResult` 对象

```python
result = await uploader.upload("/path/to/file.mp4")
print(result.file.oss_url)
print(result.deduplicated)  # 是否秒传
```

##### `calculate_md5(file, on_progress=None) -> str`

计算文件 MD5 哈希值。

```python
md5 = await uploader.calculate_md5("/path/to/file.mp4")
print(f"MD5: {md5}")
```

##### `abort_upload(file_id) -> bool`

取消上传。

```python
success = await uploader.abort_upload("file-uuid")
```

##### `get_file_info(file_id) -> FileInfo`

获取文件信息。

```python
info = await uploader.get_file_info("file-uuid")
print(info.file_name, info.file_size)
```

##### `list_files(params=None) -> tuple[list[FileInfo], int]`

获取文件列表。

```python
from community_uploader import ListFilesParams

files, total = await uploader.list_files(
    ListFilesParams(category="video", page=1, page_size=20)
)
```

##### `delete_file(file_id) -> bool`

删除文件。

```python
success = await uploader.delete_file("file-uuid")
```

##### `cancel()`

取消当前正在进行的上传。

```python
uploader.cancel()
```

### UploadOptions

上传选项配置。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `category` | `str` | "general" | 文件分类: general, video, image, document, avatar, cover |
| `content_type` | `str` | None | MIME 类型（自动检测） |
| `part_size` | `int` | None | 分片大小（字节，自动计算） |
| `metadata` | `dict` | None | 额外元数据 |
| `on_progress` | `Callable` | None | 上传进度回调 (0-100) |
| `on_md5_progress` | `Callable` | None | MD5 计算进度回调 (0-100) |

### FileInfo

文件信息对象。

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `str` | 文件 ID |
| `file_name` | `str` | 原始文件名 |
| `file_key` | `str` | OSS 文件路径 |
| `file_size` | `int` | 文件大小（字节） |
| `file_type` | `str` | MIME 类型 |
| `file_ext` | `str` | 扩展名 |
| `file_md5` | `str` | MD5 哈希 |
| `oss_url` | `str` | OSS 访问 URL |
| `cdn_url` | `str` | CDN 加速 URL |
| `category` | `str` | 文件分类 |
| `status` | `str` | 状态: pending, uploading, confirmed |
| `created_at` | `str` | 创建时间 |

### UploadResult

上传结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| `file` | `FileInfo` | 文件信息 |
| `deduplicated` | `bool` | 是否命中去重（秒传） |

## 高级用法

### 异步 Token 获取

```python
async def get_token():
    # 从 Redis 或其他异步存储获取 token
    token = await redis.get("auth_token")
    return token

uploader = CommunityUploader(
    base_url="https://api.example.com",
    get_token=get_token  # 支持异步函数
)
```

### 自定义日志

```python
import logging

logger = logging.getLogger(__name__)

uploader = CommunityUploader(
    base_url="https://api.example.com",
    get_token=lambda: "token",
    on_log=lambda msg: logger.info(msg)
)
```

### 上传字节数据

```python
# 从内存上传
video_bytes = b"..."
result = await uploader.upload(
    file=video_bytes,
    file_name="video.mp4",
    options=UploadOptions(category="video")
)
```

### 上传文件对象

```python
with open("/path/to/file.mp4", "rb") as f:
    result = await uploader.upload(
        file=f,
        file_name="video.mp4"
    )
```

### 并发控制

```python
# 增加并发数以提高速度（适合网络带宽充足的场景）
uploader = CommunityUploader(
    base_url="https://api.example.com",
    get_token=lambda: "token",
    concurrency=5  # 5 个分片并发上传
)
```

### 取消上传

```python
import asyncio

async def upload_with_timeout():
    uploader = CommunityUploader(...)

    # 创建上传任务
    upload_task = asyncio.create_task(
        uploader.upload("/path/to/large-file.mp4")
    )

    # 10 秒后取消
    await asyncio.sleep(10)
    uploader.cancel()

    try:
        result = await upload_task
    except AbortError:
        print("上传已取消")
```

## 异常处理

```python
from community_uploader import (
    UploadError,
    AuthError,
    NetworkError,
    AbortError
)

try:
    result = await uploader.upload(file)
except AuthError:
    print("认证失败，请检查 token")
except NetworkError as e:
    print(f"网络错误: {e}")
except AbortError:
    print("上传被取消")
except UploadError as e:
    print(f"上传失败: {e.message}, 错误码: {e.code}")
```

## 与 Node.js SDK 的对应关系

| Python | Node.js |
|--------|---------|
| `CommunityUploader` | `CommunityUploader` |
| `upload()` | `upload()` |
| `calculate_md5()` | `calculateMD5()` |
| `abort_upload()` | `abortUpload()` |
| `get_file_info()` | `getFileInfo()` |
| `list_files()` | `listFiles()` |
| `delete_file()` | `deleteFile()` |
| `UploadOptions` | `UploadOptions` |
| `on_progress` | `onProgress` |
| `on_md5_progress` | `onMD5Progress` |

## License

MIT
