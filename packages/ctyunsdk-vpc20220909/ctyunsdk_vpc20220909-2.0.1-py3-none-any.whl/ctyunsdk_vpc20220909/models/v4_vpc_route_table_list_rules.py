from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcRouteTableListRulesRequest(CtyunOpenAPIRequest):
    regionID: str  # 区域id
    routeTableID: str  # 路由表 id
    pageNumber: Optional[int] = None  # 列表的页码，默认值为 1。
    pageNo: Optional[int] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[int] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10。

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcRouteTableListRulesResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[List['V4VpcRouteTableListRulesReturnObj']] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcRouteTableListRulesReturnObj:
    nextHopID: Optional[str] = None  # 下一跳设备 id
    nextHopType: Optional[str] = None  # vpcpeering / havip / bm / vm / natgw/ igw6 / dc / ticc / vpngw / enic
    destination: Optional[str] = None  # 无类别域间路由
    ipVersion: Optional[int] = None  # 4 表示 ipv4, 6 表示 ipv6
    description: Optional[str] = None  # 规则描述
    routeRuleID: Optional[str] = None  # 路由规则 id
    origin: Optional[str] = None  # 路由规则来源
