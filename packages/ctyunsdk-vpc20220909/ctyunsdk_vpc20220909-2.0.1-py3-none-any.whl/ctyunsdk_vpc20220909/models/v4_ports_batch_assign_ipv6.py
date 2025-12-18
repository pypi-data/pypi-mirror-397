from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4PortsBatchAssignIpv6Request(CtyunOpenAPIRequest):
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池ID
    data: List['V4PortsBatchAssignIpv6RequestData']  # 网卡设置IPv6信息的列表

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4PortsBatchAssignIpv6RequestData:
    networkInterfaceID: str  # 网卡ID
    ipv6AddressesCount: Optional[int] = None  # Ipv6地址数量，新增自动分配地址的IPv6的数量, 与 ipv6Addresses 二选一, 最多支持 1 个
    ipv6Addresses: Optional[List[str]] = None  # IPv6地址列表，新增指定地址的IPv6列表，与 ipv6AddressesCount 二选一, 最多支持 1 个


@dataclass_json
@dataclass
class V4PortsBatchAssignIpv6Response(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


