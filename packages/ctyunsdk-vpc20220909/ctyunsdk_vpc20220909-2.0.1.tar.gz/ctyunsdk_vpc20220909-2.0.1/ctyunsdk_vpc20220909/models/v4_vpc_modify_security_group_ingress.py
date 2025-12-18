from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcModifySecurityGroupIngressRequest(CtyunOpenAPIRequest):
    regionID: str  # 区域id
    securityGroupID: str  # 安全组ID。
    securityGroupRuleID: str  # 安全组规则ID。
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    description: Optional[str] = None  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·~！@#￥%……&*（） —— -+={}|《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    remoteType: Optional[int] = None  # 远端类型，0 表示 destCidrIp，1 表示 remoteSecurityGroupID, 2 表示 prefixlistID，默认为 0
    remoteSecurityGroupID: Optional[str] = None  # 远端安全组id
    prefixListID: Optional[str] = None  # 前缀列表
    action: Optional[str] = None  # 拒绝策略:允许-accept 拒绝-drop
    priority: Optional[int] = None  # 优先级:1~100，取值越小优先级越大
    protocol: Optional[str] = None  # 协议: ANY、TCP、UDP、ICMP(v4)
    portType: Optional[int] = None  # 端口类型：0 表示 range，1 使用 port range list
    portRangeListID: Optional[str] = None  # 端口区间列表 id

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcModifySecurityGroupIngressResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


