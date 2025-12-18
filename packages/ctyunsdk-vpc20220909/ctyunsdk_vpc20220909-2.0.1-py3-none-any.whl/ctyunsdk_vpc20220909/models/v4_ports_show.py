from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4PortsShowRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    networkInterfaceID: str  # 虚拟网卡id

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4PortsShowResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4PortsShowReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4PortsShowReturnObj:
    networkInterfaceName: Optional[str] = None  # 虚拟网名称
    networkInterfaceID: Optional[str] = None  # 虚拟网id
    vpcID: Optional[str] = None  # 所属vpc
    subnetID: Optional[str] = None  # 所属子网id
    role: Optional[int] = None  # 网卡类型: 0 主网卡， 1 弹性网卡
    macAddress: Optional[str] = None  # mac地址
    primaryPrivateIp: Optional[str] = None  # 主ip
    ipv6Addresses: Optional[List[str]] = None  # ipv6地址
    instanceID: Optional[str] = None  # 关联的设备id
    instanceType: Optional[str] = None  # 设备类型 VM, BM, Other
    description: Optional[str] = None  # 描述
    securityGroupIds: Optional[List[str]] = None  # 安全组ID列表
    secondaryPrivateIps: Optional[List[str]] = None  # 辅助私网IP
    adminStatus: Optional[str] = None  # 是否启用DOWN, UP
    associatedEip: Optional['V4PortsShowReturnObjAssociatedEip'] = None  # 关联的eip信息
    privateIpDnsNameEnabled: Optional[int] = None  # 是否开启 dns
    privateIpDnsName: Optional[str] = None  # dns 名字
    sanityCheck: Optional[int] = None  # 0:检查mac,1:检查IP,2检查mac和ip


@dataclass_json
@dataclass
class V4PortsShowReturnObjAssociatedEip:
    id: Optional[str] = None  # eip id
    name: Optional[str] = None  # eip名称
