from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcListUsedIpsRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池 ID
    subnetID: str  # 子网 ID
    ip: Optional[str] = None  # 子网内的 IP 地址
    pageNumber: Optional[int] = None  # 列表的页码，默认值为 1。
    pageNo: Optional[int] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[int] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10。

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcListUsedIpsResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpcListUsedIpsReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcListUsedIpsReturnObj:
    usedIPs: Optional[List['V4VpcListUsedIpsReturnObjUsedIPs']] = None  # 已使用的 IP 数组
    totalCount: Optional[int] = None  # 列表条目数
    currentCount: Optional[int] = None  # 分页查询时每页的行数。
    totalPage: Optional[int] = None  # 总页数


@dataclass_json
@dataclass
class V4VpcListUsedIpsReturnObjUsedIPs:
    ipv4Address: Optional[str] = None  # ipv4 地址
    ipv6Address: Optional[str] = None  # ipv6 地址
    use: Optional[str] = None  # 用途：instance, pm_instance, vip, load_balance_rules, snat, ip_occupy, network:router_interface, system
    useDesc: Optional[str] = None  # 用途中文描述:云主机, 裸金属, 高可用虚 IP, SNAT, 负载均衡, 预占内网 IP, 内网网关接口, system
