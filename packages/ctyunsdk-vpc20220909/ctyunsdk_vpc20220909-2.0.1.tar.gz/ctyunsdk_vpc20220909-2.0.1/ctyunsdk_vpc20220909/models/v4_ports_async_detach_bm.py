from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4PortsAsyncDetachBmRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    azName: str  # 可用区
    networkInterfaceID: str  # 网卡ID
    instanceID: str  # 绑定实例ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4PortsAsyncDetachBmResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4PortsAsyncDetachBmReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4PortsAsyncDetachBmReturnObj:
    status: Optional[str] = None  # 状态。in_progress表示在异步处理中，done成功
    message: Optional[str] = None  # 当前状态的中文说明
