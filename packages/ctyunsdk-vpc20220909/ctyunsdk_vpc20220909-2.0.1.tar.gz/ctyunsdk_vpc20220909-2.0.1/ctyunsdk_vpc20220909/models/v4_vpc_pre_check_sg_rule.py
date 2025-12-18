from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcPreCheckSgRuleRequest(CtyunOpenAPIRequest):
    regionID: str  # 区域 id
    securityGroupID: str  # 安全组 ID。
    securityGroupRule: 'V4VpcPreCheckSgRuleRequestSecurityGroupRule'  # 规则信息

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcPreCheckSgRuleRequestSecurityGroupRule:
    direction: str  # 入方向
    action: str  # 拒绝策略:允许-accept 拒绝-drop
    protocol: str  # 协议: ANY、TCP、UDP、ICMP(v4)
    ethertype: str  # IP 类型:IPv4、IPv6
    destCidrIp: str  # 远端地址:0.0.0.0/0
    priority: Optional[int] = None  # 优先级:1~100，取值越小优先级越大
    description: Optional[str] = None  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&_()_-+= <>?:"{},./;'[]·~！@#￥%……&_（） —— -+={}|《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    range: Optional[str] = None  # 安全组开放的传输层协议相关的源端端口范围


@dataclass_json
@dataclass
class V4VpcPreCheckSgRuleResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpcPreCheckSgRuleReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcPreCheckSgRuleReturnObj:
    sgRuleID: Optional[str] = None  # 和哪个规则重复
