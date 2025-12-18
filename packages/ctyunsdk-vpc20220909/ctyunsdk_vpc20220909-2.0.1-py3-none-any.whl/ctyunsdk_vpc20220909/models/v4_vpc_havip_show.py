from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcHavipShowRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池 ID
    haVipID: str  # 高可用虚 IP 的 ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcHavipShowResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpcHavipShowReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcHavipShowReturnObj:
    id: Optional[str] = None  # 高可用虚 IP 的 ID
    ipv4: Optional[str] = None  # IPv4 地址
    ipv6: Optional[str] = None  # ipv6 地址
    vpcID: Optional[str] = None  # 虚拟私有云的的 id
    subnetID: Optional[str] = None  # 子网 id
    instanceInfo: Optional[List['V4VpcHavipShowReturnObjInstanceInfo']] = None  # 绑定实例相关信息
    networkInfo: Optional[List['V4VpcHavipShowReturnObjNetworkInfo']] = None  # 绑定弹性 IP 相关信息
    bindPorts: Optional[List['V4VpcHavipShowReturnObjBindPorts']] = None  # 绑定网卡信息


@dataclass_json
@dataclass
class V4VpcHavipShowReturnObjInstanceInfo:
    instanceName: Optional[str] = None  # 实例名
    id: Optional[str] = None  # 实例 ID
    privateIp: Optional[str] = None  # 实例私有 IP
    privateIpv6: Optional[str] = None  # 实例的 IPv6 地址, 可以为空字符串
    publicIp: Optional[str] = None  # 实例公网 IP


@dataclass_json
@dataclass
class V4VpcHavipShowReturnObjNetworkInfo:
    eipID: Optional[str] = None  # 弹性 IP ID


@dataclass_json
@dataclass
class V4VpcHavipShowReturnObjBindPorts:
    portID: Optional[str] = None  # 网卡 ID
    role: Optional[str] = None  # keepalive 角色: master / slave
    createdAt: Optional[str] = None  # 创建时间
