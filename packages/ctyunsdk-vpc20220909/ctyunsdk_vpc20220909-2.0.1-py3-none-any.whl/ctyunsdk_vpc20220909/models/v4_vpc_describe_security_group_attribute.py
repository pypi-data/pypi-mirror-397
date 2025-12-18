from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcDescribeSecurityGroupAttributeRequest(CtyunOpenAPIRequest):
    regionID: str  # 区域id
    securityGroupID: str  # 安全组ID
    projectID: Optional[str] = None  # 企业项目 ID，默认为0
    direction: Optional[str] = None  # 安全组规则授权方向：</br>&#32;egress：安全组出方向  </br>&#32;ingress：安全组入方向 </br>&#32;all：不区分方向 默认是：all

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcDescribeSecurityGroupAttributeResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpcDescribeSecurityGroupAttributeReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcDescribeSecurityGroupAttributeReturnObj:
    securityGroupName: Optional[str] = None  # 安全组名称
    id: Optional[str] = None  # 安全组id
    vmNum: Optional[int] = None  # 相关云主机
    origin: Optional[str] = None  # 表示是否是默认安全组
    vpcName: Optional[str] = None  # vpc名称
    vpcID: Optional[str] = None  # 安全组所属的专有网络。
    creationTime: Optional[str] = None  # 创建时间
    description: Optional[str] = None  # 安全组描述信息。
    projectID: Optional[str] = None  # 项目ID
    securityGroupRuleList: Optional[List['V4VpcDescribeSecurityGroupAttributeReturnObjSecurityGroupRuleList']] = None  # 安全组规则信息


@dataclass_json
@dataclass
class V4VpcDescribeSecurityGroupAttributeReturnObjSecurityGroupRuleList:
    direction: Optional[str] = None  # 出方向-egress、入方向-ingress
    priority: Optional[int] = None  # 优先级:0~100
    ethertype: Optional[str] = None  # IP类型:IPv4、IPv6
    protocol: Optional[str] = None  # 协议: ANY、TCP、UDP、ICMP、ICMP6
    range: Optional[str] = None  # 接口范围/ICMP类型:1-65535
    destCidrIp: Optional[str] = None  # 远端地址:0.0.0.0/0
    description: Optional[str] = None  # 安全组规则描述信息。
    createTime: Optional[str] = None  # 创建时间，UTC时间。
    id: Optional[str] = None  # 唯一标识ID
    securityGroupID: Optional[str] = None  # 安全组ID
    action: Optional[str] = None  # 拒绝策略:允许-accept 拒绝-drop
    origin: Optional[str] = None  # 类型
    remoteSecurityGroupID: Optional[str] = None  # 远端安全组id
    prefixListID: Optional[str] = None  # 前缀列表id
