"""
异常定义
"""


class UploadError(Exception):
    """上传错误基类"""

    def __init__(self, message: str, code: int = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class AuthError(UploadError):
    """认证错误"""
    pass


class NetworkError(UploadError):
    """网络错误"""
    pass


class AbortError(UploadError):
    """上传被取消"""

    def __init__(self, message: str = "上传已取消"):
        super().__init__(message)
