from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4PortsNewListRequest(CtyunOpenAPIRequest):
    regionID: str  # 区域id
    vpcID: Optional[str] = None  # 所属vpc id
    deviceID: Optional[str] = None  # 关联设备id
    subnetID: Optional[str] = None  # 所属子网id
    pageNumber: Optional[int] = None  # 列表的页码，默认值为 1。
    pageNo: Optional[int] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[int] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10。

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4PortsNewListResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4PortsNewListReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4PortsNewListReturnObj:
    ports: Optional[List['V4PortsNewListReturnObjPorts']] = None  # 网卡列表
    totalCount: Optional[int] = None  # 列表条目数
    currentCount: Optional[int] = None  # 分页查询时每页的行数。
    totalPage: Optional[int] = None  # 总页数


@dataclass_json
@dataclass
class V4PortsNewListReturnObjPorts:
    networkInterfaceName: Optional[str] = None  # 虚拟网名称
    networkInterfaceID: Optional[str] = None  # 虚拟网id
    vpcID: Optional[str] = None  # 所属vpc
    subnetID: Optional[str] = None  # 所属子网id
    role: Optional[int] = None  # 网卡类型: 0 主网卡， 1 弹性网卡
    macAddress: Optional[str] = None  # mac地址
    primaryPrivateIp: Optional[str] = None  # 主ip
    ipv6Addresses: Optional[List[str]] = None  # ipv6地址
    instanceID: Optional[str] = None  # 关联的设备id
    instanceType: Optional[str] = None  # 设备类型 VM(云主机), BM(裸金属), LB(弹性负载均衡), CBM(标准裸金属)
    description: Optional[str] = None  # 描述
    securityGroupIds: Optional[List[str]] = None  # 安全组ID列表
    secondaryPrivateIps: Optional[List[str]] = None  # 辅助私网IP
    adminStatus: Optional[str] = None  # 是否启用DOWN, UP
    privateIpDnsNameEnabled: Optional[int] = None  # 是否开启 dns
    privateIpDnsName: Optional[str] = None  # dns 名字
