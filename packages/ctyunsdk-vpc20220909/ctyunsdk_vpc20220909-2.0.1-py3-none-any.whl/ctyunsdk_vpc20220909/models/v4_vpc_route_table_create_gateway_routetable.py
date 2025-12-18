from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcRouteTableCreateGatewayRoutetableRequest(CtyunOpenAPIRequest):
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域id
    vpcID: str  # 关联的vpcID
    name: str  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    description: Optional[str] = None  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·~！@#￥%……&*（） —— -+={}|《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcRouteTableCreateGatewayRoutetableResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpcRouteTableCreateGatewayRoutetableReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcRouteTableCreateGatewayRoutetableReturnObj:
    name: Optional[str] = None  # 路由表名字
    description: Optional[str] = None  # 路由表描述
    vpcID: Optional[str] = None  # 虚拟私有云 id
    id: Optional[str] = None  # 路由 id
    routeRulesCount: Optional[int] = None  # 路由规则数量
    createdAt: Optional[str] = None  # 创建时间
    updatedAt: Optional[str] = None  # 更新时间
