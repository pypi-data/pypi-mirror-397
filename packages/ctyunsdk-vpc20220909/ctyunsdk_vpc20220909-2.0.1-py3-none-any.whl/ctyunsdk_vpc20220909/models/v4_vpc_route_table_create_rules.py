from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcRouteTableCreateRulesRequest(CtyunOpenAPIRequest):
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域id
    routeTableID: str  # 路由表 id
    routeRules: List['V4VpcRouteTableCreateRulesRequestRouteRules']  # 路由表规则列表

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcRouteTableCreateRulesRequestRouteRules:
    nextHopID: str  # 下一跳设备 id
    nextHopType: str  # vpcpeering / havip / bm / vm / natgw/ igw6 / dc / ticc / vpngw / enic / gwlbe
    destination: str  # 无类别域间路由
    ipVersion: int  # 4 标识 ipv4, 6 标识 ipv6
    description: Optional[str] = None  # 规则描述


@dataclass_json
@dataclass
class V4VpcRouteTableCreateRulesResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[List[str]] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


