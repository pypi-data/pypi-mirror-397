from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcQueryRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池 ID
    vpcID: str  # VPC 的 ID
    projectID: Optional[str] = None  # 企业项目 ID，默认为0

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcQueryResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpcQueryReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcQueryReturnObj:
    vpcID: Optional[str] = None  # vpc 示例 ID
    name: Optional[str] = None  # 名称
    description: Optional[str] = None  # 描述
    CIDR: Optional[str] = None  # CIDR
    ipv6Enabled: Optional[bool] = None  # 是否开启 ipv6
    enableIpv6: Optional[bool] = None  # 是否开启 ipv6
    ipv6CIDRS: Optional[List[str]] = None  # ipv6CIDRS
    subnetIDs: Optional[List[str]] = None  # 子网 id 列表
    natGatewayIDs: Optional[List[str]] = None  # 网关 id 列表
    secondaryCIDRS: Optional[List[str]] = None  # 附加网段
    projectID: Optional[str] = None  # 企业项目 ID，默认为0
    dhcpOptionsSetID: Optional[str] = None  # VPC关联的dhcp选项集
    ipv6Infos: Optional[List[object]] = None  # vpc ipv6网段列表
