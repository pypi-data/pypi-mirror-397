from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcHavipListRequest(CtyunOpenAPIRequest):
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池ID
    projectID: Optional[str] = None  # 企业项目ID，默认为"0"
    filters: Optional[List['V4VpcHavipListRequestFilters']] = None  # 筛选条件,filters为一个表，{key:haVipID(vpcID,subnetID),value:xxx(筛选字段对应key的value)},具体见请求体body示例

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcHavipListRequestFilters:
    key: str  # 筛选字段的key，支持：haVipID，vpcID，subnetID
    value: str  # 筛选字段对应key的value


@dataclass_json
@dataclass
class V4VpcHavipListResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[List['V4VpcHavipListReturnObj']] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcHavipListReturnObj:
    id: Optional[str] = None  # 高可用虚IP的ID
    ipv4: Optional[str] = None  # IPv4地址
    vpcID: Optional[str] = None  # 虚拟私有云的的id
    subnetID: Optional[str] = None  # 子网id
    instanceInfo: Optional[List['V4VpcHavipListReturnObjInstanceInfo']] = None  # 绑定实例相关信息
    networkInfo: Optional[List['V4VpcHavipListReturnObjNetworkInfo']] = None  # 绑定弹性 IP 相关信息


@dataclass_json
@dataclass
class V4VpcHavipListReturnObjInstanceInfo:
    instanceName: Optional[str] = None  # 实例名
    id: Optional[str] = None  # 实例 ID
    privateIp: Optional[str] = None  # 实例私有 IP
    privateIpv6: Optional[str] = None  # 实例的 IPv6 地址, 可以为空字符串
    publicIp: Optional[str] = None  # 实例公网 IP


@dataclass_json
@dataclass
class V4VpcHavipListReturnObjNetworkInfo:
    eipID: Optional[str] = None  # 弹性 IP ID
