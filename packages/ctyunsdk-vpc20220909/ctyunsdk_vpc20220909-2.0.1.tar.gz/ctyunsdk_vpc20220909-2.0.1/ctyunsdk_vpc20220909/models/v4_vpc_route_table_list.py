from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcRouteTableListRequest(CtyunOpenAPIRequest):
    regionID: str  # 区域id
    vpcID: Optional[str] = None  # 关联的vpcID
    queryContent: Optional[str] = None  # 对路由表名字 / 路由表描述 / 路由表 id 进行模糊查询
    routeTableID: Optional[str] = None  # 路由表 id
    type: Optional[int] = None  # 路由表类型:0-子网路由表；2-网关路由表
    pageNumber: Optional[int] = None  # 列表的页码，默认值为 1。
    pageNo: Optional[int] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[int] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10。

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcRouteTableListResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[List['V4VpcRouteTableListReturnObj']] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcRouteTableListReturnObj:
    name: Optional[str] = None  # 路由表名字
    description: Optional[str] = None  # 路由表描述
    vpcID: Optional[str] = None  # 虚拟私有云 id
    id: Optional[str] = None  # 路由 id
    freezing: Optional[bool] = None  # 是否冻结
    routeRulesCount: Optional[int] = None  # 路由表中的路由数
    createdAt: Optional[str] = None  # 创建时间
    updatedAt: Optional[str] = None  # 更新时间
    type: Optional[int] = None  # 路由表类型:0-子网路由表，2-网关路由表
    ipv4Gw: Optional['V4VpcRouteTableListReturnObjIpv4Gw'] = None  # 绑定的IPv4网关信息（未绑定时未null）
    origin: Optional[str] = None  # 路由表来源：default-系统默认; user-用户创建
    subnetLocalRouteEnabled: Optional[int] = None  # 是否开启子网local路由，0 关闭，1 开启


@dataclass_json
@dataclass
class V4VpcRouteTableListReturnObjIpv4Gw:
    id: Optional[str] = None  # IPv4网关的ID
    name: Optional[str] = None  # IPv4网关名称
