from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcNewListSubnetRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池 ID
    vpcID: str  # VPC 的 ID
    clientToken: Optional[str] = None  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    subnetID: Optional[str] = None  # 多个 subnet 的 ID 之间用半角逗号（,）隔开。
    pageNumber: Optional[int] = None  # 列表的页码，默认值为 1。
    pageNo: Optional[int] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[int] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10。
    withShare: Optional[bool] = None  # 是否查询共享信息
    subnetName: Optional[str] = None  # 子网名字
    cidr: Optional[str] = None  # cidr

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcNewListSubnetResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpcNewListSubnetReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcNewListSubnetReturnObj:
    subnets: Optional[List['V4VpcNewListSubnetReturnObjSubnets']] = None  # subnets 组
    totalCount: Optional[int] = None  # 列表条目数
    currentCount: Optional[int] = None  # 分页查询时每页的行数。
    totalPage: Optional[int] = None  # 总页数


@dataclass_json
@dataclass
class V4VpcNewListSubnetReturnObjSubnets:
    subnetID: Optional[str] = None  # subnet ID
    name: Optional[str] = None  # 名称
    description: Optional[str] = None  # 描述
    vpcID: Optional[str] = None  # VpcID
    availabilityZones: Optional[List[str]] = None  # 子网所在的可用区名
    routeTableID: Optional[str] = None  # 子网路由表 ID
    networkAclID: Optional[str] = None  # 子网 aclID
    CIDR: Optional[str] = None  # 子网网段，掩码范围为 16-28 位
    gatewayIP: Optional[str] = None  # 子网网关
    start: Optional[str] = None  # 子网网段起始 IP
    end: Optional[str] = None  # 子网网段结束 IP
    availableIPCount: Optional[int] = None  # 子网内可用 IPv4 数目
    ipv6Enabled: Optional[int] = None  # 是否配置了ipv6网段
    enableIpv6: Optional[bool] = None  # 是否开启 ipv6
    ipv6CIDR: Optional[str] = None  # 子网 Ipv6 网段，掩码范围为 16-28 位
    ipv6Start: Optional[str] = None  # 子网内可用的起始 IPv6 地址
    ipv6End: Optional[str] = None  # 子网内可用的结束 IPv6 地址
    ipv6GatewayIP: Optional[str] = None  # v6 网关地址
    dnsList: Optional[List[str]] = None  # DNS 服务器地址:默认为空；必须为正确的 IPv4 格式；重新触发 DHCP 后生效，最大数组长度为 4
    systemDnsList: Optional[List[str]] = None  # 系统自带DNS服务器地址
    ntpList: Optional[List[str]] = None  # NTP 服务器地址: 默认为空，必须为正确的域名或 IPv4 格式；重新触发 DHCP 后生效，最大数组长度为 4
    type: Optional[int] = None  # 子网类型 :当前仅支持：0（普通子网）, 1（裸金属子网）
    updatedAt: Optional[str] = None  # 更新时间
    ipv6Info: Optional[object] = None  # 子网ipv6网段信息
