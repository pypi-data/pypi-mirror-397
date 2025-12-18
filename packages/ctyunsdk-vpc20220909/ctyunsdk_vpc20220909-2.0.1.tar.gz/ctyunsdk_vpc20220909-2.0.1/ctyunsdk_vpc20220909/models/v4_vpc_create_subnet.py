from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcCreateSubnetRequest(CtyunOpenAPIRequest):
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池 ID
    vpcID: str  # 虚拟私有云 ID
    name: str  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    CIDR: str  # 子网网段
    description: Optional[str] = None  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·~！@#￥%……&*（） —— -+={}|《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    enableIpv6: Optional[bool] = None  # 是否开启 IPv6 网段。取值：false（默认值）:不开启，true: 开启
    dnsList: Optional[List[str]] = None  # 子网 dns 列表, 最多同时支持 4 个 dns 地址
    subnetGatewayIP: Optional[str] = None  # 子网网关 IP
    dhcpIP: Optional[str] = None  # 网关DHCP,和网关IP不能相同
    subnetType: Optional[str] = None  # 子网类型：common（普通子网）/ cbm（裸金属子网），默认为普通子网
    vpcIpv6CIDR: Optional[str] = None  # vpc ipv6 CIDR
    ipv6CIDR: Optional[str] = None  # subnet ipv6 CIDR
    routeTableID: Optional[str] = None  # 路由表 ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcCreateSubnetResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpcCreateSubnetReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcCreateSubnetReturnObj:
    subnetID: Optional[str] = None  # subnet 示例 ID
