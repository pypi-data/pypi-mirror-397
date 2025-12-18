from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcUpdateIpv6StatusRequest(CtyunOpenAPIRequest):
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池 ID
    vpcID: str  # VPC 的
    enableIpv6: bool  # 是否开启 IPv6 网段。取值：false（默认值）:不开启，true: 开启
    projectID: Optional[str] = None  # 企业项目 ID，默认为"0"
    addressPoolType: Optional[str] = None  # 地址池类型: custom or ctyun
    ipv6SegmentPoolID: Optional[str] = None  # ipv6 segment pool id
    ipv6Isp: Optional[str] = None  # isp类型
    vpcIpv6CIDR: Optional[str] = None  # vpc ipv6 CIDR

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcUpdateIpv6StatusResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


