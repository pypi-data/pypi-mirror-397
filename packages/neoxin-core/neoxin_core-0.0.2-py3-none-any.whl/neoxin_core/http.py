"""
HTTP模块

提供统一的HTTP响应处理功能。
"""

from typing import Any, Optional, Dict
from fastapi import status
from fastapi.responses import JSONResponse
from .schemas import ApiResponse, PaginatedResponse


class ResponseHandler:
    """
    统一响应处理器

    提供统一的HTTP响应处理功能。通过该处理器，可以方便地生成统一的JSON响应，包括成功、错误、创建、未找到、未授权等常见场景。


    """

    @staticmethod
    def success(
        data: Any = None, message: str = "操作成功", code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """
        成功响应

        Args:
            data (Any, optional): 数据. Defaults to None.
            message (str, optional): 消息. Defaults to "操作成功".
            code (int, optional): 状态码. Defaults to status.HTTP_200_OK.
        """
        response_data = ApiResponse(code=code, message=message, data=data, error=None)
        return JSONResponse(
            status_code=code,
            content=response_data.model_dump(
                mode="json", exclude_none=True, by_alias=True
            ),
        )

    @staticmethod
    def error(
        message: str,
        code: int = status.HTTP_400_BAD_REQUEST,
        error_details: Optional[Dict[str, Any]] = None,
    ) -> JSONResponse:
        """
        错误响应

        Args:
            message (str): 消息
            code (int, optional): 状态码. Defaults to status.HTTP_400_BAD_REQUEST.
            error_details (Optional[Dict[str, Any]], optional): 错误详情. Defaults to None.
        """
        response_data = ApiResponse(
            code=code, message=message, error=error_details, data=None
        )
        return JSONResponse(
            status_code=code,
            content=response_data.model_dump(
                mode="json", exclude_none=True, by_alias=True
            ),
        )

    @staticmethod
    def created(data: Any = None, message: str = "创建成功") -> JSONResponse:
        """
        创建成功响应

        Args:
            data (Any, optional): 数据. Defaults to None.
            message (str, optional): 消息. Defaults to "创建成功".
        """
        return ResponseHandler.success(
            data=data, message=message, code=status.HTTP_201_CREATED
        )

    @staticmethod
    def not_found(
        message: str = "资源未找到", error_details: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        资源未找到响应

        Args:
            message (str, optional): 消息. Defaults to "资源未找到".
            error_details (Optional[Dict[str, Any]], optional): 错误详情. Defaults to None.
        """
        return ResponseHandler.error(
            message=message, code=status.HTTP_404_NOT_FOUND, error_details=error_details
        )

    @staticmethod
    def unauthorized(
        message: str = "未授权访问", error_details: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        未授权响应

        Args:
            message (str, optional): 消息. Defaults to "未授权访问".
            error_details (Optional[Dict[str, Any]], optional): 错误详情. Defaults to None.
        """
        return ResponseHandler.error(
            message=message,
            code=status.HTTP_401_UNAUTHORIZED,
            error_details=error_details,
        )

    @staticmethod
    def forbidden(
        message: str = "权限不足", error_details: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        权限不足响应

        Args:
            message (str, optional): 消息. Defaults to "权限不足".
            error_details (Optional[Dict[str, Any]], optional): 错误详情. Defaults to None.
        """
        return ResponseHandler.error(
            message=message, code=status.HTTP_403_FORBIDDEN, error_details=error_details
        )

    @staticmethod
    def validation_error(
        message: str = "数据验证失败", error_details: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        数据验证错误响应

        Args:
            message (str, optional): 消息. Defaults to "".
            error_details (Optional[Dict[str, Any]], optional): 错误详情. Defaults to None.
        """
        return ResponseHandler.error(
            message=message,
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_details=error_details,
        )

    @staticmethod
    def internal_error(
        message: str = "服务器内部错误", error_details: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        服务器内部错误响应

        Args:
            message (str, optional): 消息. Defaults to "服务器内部错误".
            error_details (Optional[Dict[str, Any]], optional): 错误详情. Defaults to None.
        """
        return ResponseHandler.error(
            message=message,
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_details=error_details,
        )


# 便捷的响应函数
def success_response(
    data: Any = None, message: str = "操作成功", code: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    成功响应便捷函数

    Args:
        data (Any, optional): 数据. Defaults to None.
        message (str, optional): 消息. Defaults to "操作成功".
        code (int, optional): 状态码. Defaults to status.HTTP_200_OK.
    """
    return ResponseHandler.success(data, message, code)


def error_response(
    message: str,
    code: int = status.HTTP_400_BAD_REQUEST,
    error_details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """
    错误响应便捷函数

    Args:
        message (str): 消息
        code (int, optional): 状态码. Defaults to status.HTTP_400_BAD_REQUEST.
        error_details (Optional[Dict[str, Any]], optional): 错误详情. Defaults to None.
    """
    return ResponseHandler.error(message, code, error_details)


def paginated_response(
    data: PaginatedResponse, message: str = "查询成功"
) -> JSONResponse:
    """
    分页响应便捷函数

    Args:
        data (PaginatedResponse): 分页数据
        message (str, optional): 消息. Defaults to "查询成功".
    """
    return success_response(
        data=data.model_dump(mode="json", exclude_none=True, by_alias=True),
        message=message,
    )


# 别名函数，为了兼容性
create_success_response = success_response
