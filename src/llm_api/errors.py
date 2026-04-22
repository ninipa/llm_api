class LlmApiError(Exception):
    """项目内所有对外错误的基类。"""


class ConfigurationError(LlmApiError):
    """配置缺失或配置值不合法。"""


class RequestError(LlmApiError):
    """远端请求失败。"""


class ResponseFormatError(LlmApiError):
    """响应结构不符合预期。"""
