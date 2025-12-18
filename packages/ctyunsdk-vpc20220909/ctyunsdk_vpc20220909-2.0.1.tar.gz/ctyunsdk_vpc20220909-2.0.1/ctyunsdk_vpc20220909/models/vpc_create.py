from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class VpcCreateRequest(CtyunOpenAPIRequest):
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池 ID
    name: str  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    CIDR: str  # VPC 的网段。建议您使用 192.168.0.0/16、172.16.0.0/12、10.0.0.0/8 三个 RFC 标准私网网段及其子网作为专有网络的主 IPv4 网段，网段掩码有效范围为 8~28 位，不能使用预占网段
    projectID: Optional[str] = None  # 企业项目 ID，默认为0
    description: Optional[str] = None  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·~！@#￥%……&*（） —— -+={}|《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    enableIpv6: Optional[bool] = None  # 是否开启 IPv6 网段。取值：false（默认值）:不开启，true: 开启
    ipv6SegmentPoolID: Optional[str] = None  # 地址段ID, addressPoolType=custom时必传
    addressPoolType: Optional[str] = None  # 地址池类型: custom or ctyun
    ipv6Cidr: Optional[str] = None  # ipv6 CIDR
    ipv6Isp: Optional[str] = None  # ipv6 ISP: chinatelecom,chinamobile等, addressPoolType=custom时参数无效,ctyun时,参数必传

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class VpcCreateResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['VpcCreateReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class VpcCreateReturnObj:
    vpcID: Optional[str] = None  # vpc 示例 ID
