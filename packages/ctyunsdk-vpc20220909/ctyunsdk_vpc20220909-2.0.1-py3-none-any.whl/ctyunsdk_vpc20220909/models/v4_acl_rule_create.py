from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4AclRuleCreateRequest(CtyunOpenAPIRequest):
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池ID
    aclID: str  # aclID
    rules: List['V4AclRuleCreateRequestRules']  # rule 规则数组

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4AclRuleCreateRequestRules:
    direction: str  # 类型,ingress, egress
    protocol: str  # all, icmp, tcp, udp, gre,  icmp6
    ipVersion: str  # ipv4,  ipv6
    sourceIpAddress: str  # 源地址
    destinationIpAddress: str  # 目的地址
    action: str  # accept, drop
    enabled: str  # disable, enable
    priority: Optional[int] = None  # 优先级 1 - 32766，不填默认100
    destinationPort: Optional[str] = None  # 开始和结束port以:隔开
    sourcePort: Optional[str] = None  # 开始和结束port以:隔开
    description: Optional[str] = None  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:'{},./;'[,]·！@#￥%……&*（） —— -+={},《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128


@dataclass_json
@dataclass
class V4AclRuleCreateResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4AclRuleCreateReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4AclRuleCreateReturnObj:
    aclID: Optional[str] = None  # 名称
