from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4AclRuleListRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    aclID: str  # aclID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4AclRuleListResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4AclRuleListReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4AclRuleListReturnObj:
    aclID: Optional[str] = None  # id
    name: Optional[str] = None  # 名称
    description: Optional[str] = None  # 描述
    vpcID: Optional[str] = None  # VPC
    enabled: Optional[str] = None  # disable,enable
    inPolicyID: Optional[List[str]] = None  # 入规则id数组
    outPolicyID: Optional[List[str]] = None  # 出规则id数组
    inRules: Optional[List['V4AclRuleListReturnObjInRules']] = None  # 出规则id数组
    outRules: Optional[List['V4AclRuleListReturnObjOutRules']] = None  # 出规则id数组
    createdAt: Optional[str] = None  # 创建时间
    updatedAt: Optional[str] = None  # 更新时间
    subnetIDs: Optional[List[str]] = None  # acl 绑定的子网 id


@dataclass_json
@dataclass
class V4AclRuleListReturnObjInRules:
    aclRuleID: Optional[str] = None  # aclRuleID
    direction: Optional[str] = None  # 类型,ingress, egress
    priority: Optional[int] = None  # 优先级
    protocol: Optional[str] = None  # all, icmp, tcp, udp, gre,  icmp6
    ipVersion: Optional[str] = None  # ipv4,  ipv6
    destinationPort: Optional[str] = None  # 开始和结束port以:隔开
    sourcePort: Optional[str] = None  # 开始和结束port以:隔开
    sourceIpAddress: Optional[str] = None  # 类型,ingress, egress
    destinationIpAddress: Optional[str] = None  # 类型,ingress, egress
    action: Optional[str] = None  # accept, drop
    enabled: Optional[str] = None  # disable, enable
    description: Optional[str] = None  # 描述


@dataclass_json
@dataclass
class V4AclRuleListReturnObjOutRules:
    aclRuleID: Optional[str] = None  # aclRuleID
    direction: Optional[str] = None  # 类型,ingress, egress
    priority: Optional[int] = None  # 优先级
    protocol: Optional[str] = None  # all, icmp, tcp, udp, gre,  icmp6
    ipVersion: Optional[str] = None  # ipv4,  ipv6
    destinationPort: Optional[str] = None  # 开始和结束port以:隔开
    sourcePort: Optional[str] = None  # 开始和结束port以:隔开
    sourceIpAddress: Optional[str] = None  # 类型,ingress, egress
    destinationIpAddress: Optional[str] = None  # 类型,ingress, egress
    action: Optional[str] = None  # accept, drop
    enabled: Optional[str] = None  # disable, enable
    description: Optional[str] = None  # 描述
