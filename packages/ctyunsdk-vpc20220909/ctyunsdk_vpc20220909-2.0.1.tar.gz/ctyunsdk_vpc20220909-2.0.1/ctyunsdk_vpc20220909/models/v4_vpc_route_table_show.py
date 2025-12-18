from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcRouteTableShowRequest(CtyunOpenAPIRequest):
    regionID: str  # 区域id
    routeTableID: str  # 路由表 id

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcRouteTableShowResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpcRouteTableShowReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcRouteTableShowReturnObj:
    name: Optional[str] = None  # 路由表名字
    description: Optional[str] = None  # 路由表描述
    vpcID: Optional[str] = None  # 虚拟私有云 id
    id: Optional[str] = None  # 路由 id
    freezing: Optional[bool] = None  # 是否冻结
    routeRulesCount: Optional[int] = None  # 路由表中的路由数
    createdAt: Optional[str] = None  # 创建时间
    updatedAt: Optional[str] = None  # 更新时间
    routeRules: Optional[List[str]] = None  # 路由规则 id 列表
    subnetDetail: Optional[List['V4VpcRouteTableShowReturnObjSubnetDetail']] = None  # 子网配置详情
    type: Optional[int] = None  # 路由表类型:0-子网路由表，2-网关路由表
    ipv4Gw: Optional['V4VpcRouteTableShowReturnObjIpv4Gw'] = None  # 绑定的IPv4网关信息
    origin: Optional[str] = None  # 路由表来源：default-系统默认; user-用户创建
    subnetLocalRouteEnabled: Optional[int] = None  # 是否开启子网local路由，0 关闭，1 开启


@dataclass_json
@dataclass
class V4VpcRouteTableShowReturnObjSubnetDetail:
    id: Optional[str] = None  # 路由下子网 id
    name: Optional[str] = None  # 路由下子网名字
    cidr: Optional[str] = None  # ipv4 无类别域间路由
    ipv6Cidr: Optional[str] = None  # ipv6 无类别域间路由


@dataclass_json
@dataclass
class V4VpcRouteTableShowReturnObjIpv4Gw:
    id: Optional[str] = None  # IPv4网关 id
    name: Optional[str] = None  # IPv4网关名称
