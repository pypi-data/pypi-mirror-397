from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4PortsCreateRequest(CtyunOpenAPIRequest):
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池ID
    subnetID: str  # 子网ID
    primaryPrivateIp: Optional[str] = None  # 弹性网卡的主私有IP地址
    ipv6Addresses: Optional[List[str]] = None  # 为弹性网卡指定一个或多个IPv6地址
    securityGroupIds: Optional[List[str]] = None  # 加入一个或多个安全组。安全组和弹性网卡必须在同一个专有网络VPC中，最多同时支持 10 个
    secondaryPrivateIpCount: Optional[int] = None  # 指定私有IP地址数量，让ECS为您自动创建IP地址
    secondaryPrivateIps: Optional[List[str]] = None  # 指定私有IP地址，不能和secondaryPrivateIpCount同时指定
    name: Optional[str] = None  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    description: Optional[str] = None  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·~！@#￥%……&*（） —— -+={}\《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    privateIpDnsNameEnabled: Optional[int] = None  # 是否开启 dns
    labels: Optional[List[object]] = None  # 标签

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4PortsCreateResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4PortsCreateReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4PortsCreateReturnObj:
    vpcID: Optional[str] = None  # vpc的id
    subnetID: Optional[str] = None  # 子网id
    networkInterfaceID: Optional[str] = None  # 网卡id
    networkInterfaceName: Optional[str] = None  # 网卡名称
    macAddress: Optional[str] = None  # mac地址
    description: Optional[str] = None  # 网卡描述
    ipv6Address: Optional[List[str]] = None  # IPv6地址列表
    securityGroupIds: Optional[List[str]] = None  # 安全组ID列表
    secondaryPrivateIps: Optional[List[str]] = None  # 二级IP地址列表
    privateIpAddress: Optional[str] = None  # 弹性网卡的主私有IP
    instanceOwnerID: Optional[str] = None  # 绑定的实例的所有者ID
    instanceType: Optional[str] = None  # 设备类型 VM, BM, Other
    instanceID: Optional[str] = None  # 绑定的实例ID
