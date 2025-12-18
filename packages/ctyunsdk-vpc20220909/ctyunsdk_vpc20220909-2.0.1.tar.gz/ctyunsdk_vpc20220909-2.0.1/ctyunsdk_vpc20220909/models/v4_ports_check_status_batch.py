from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4PortsCheckStatusBatchRequest(CtyunOpenAPIRequest):
    regionID: str  # 区域id
    portIDs: str  # 多个网卡用 , 拼接起来, port-id,port-id, 最多支持同时检查 10 个网卡

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4PortsCheckStatusBatchResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[List['V4PortsCheckStatusBatchReturnObj']] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4PortsCheckStatusBatchReturnObj:
    id: Optional[str] = None  # 网卡 id
    status: Optional[str] = None  # 网卡状态
