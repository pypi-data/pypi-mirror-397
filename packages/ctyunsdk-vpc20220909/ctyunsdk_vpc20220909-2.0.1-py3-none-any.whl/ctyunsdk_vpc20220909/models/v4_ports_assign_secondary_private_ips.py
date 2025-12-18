from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4PortsAssignSecondaryPrivateIpsRequest(CtyunOpenAPIRequest):
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池ID
    networkInterfaceID: str  # 弹性网卡ID
    secondaryPrivateIps: Optional[List[str]] = None  # 辅助私网IP列表，新增辅助私网IP, 最多支持 15 个
    secondaryPrivateIpCount: Optional[int] = None  # 辅助私网IP数量，新增自动分配辅助私网IP的数量, 最多支持 15 个

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4PortsAssignSecondaryPrivateIpsResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4PortsAssignSecondaryPrivateIpsReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4PortsAssignSecondaryPrivateIpsReturnObj:
    secondaryPrivateIps: Optional[List[str]] = None  # 分配的私网 ip 地址
