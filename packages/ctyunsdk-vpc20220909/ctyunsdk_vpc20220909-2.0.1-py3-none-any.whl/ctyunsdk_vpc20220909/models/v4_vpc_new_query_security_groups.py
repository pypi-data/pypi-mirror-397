from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcNewQuerySecurityGroupsRequest(CtyunOpenAPIRequest):
    regionID: str
    vpcID: Optional[str] = None
    queryContent: Optional[str] = None
    instanceID: Optional[str] = None
    pageNumber: Optional[int] = None  # 1
    pageNo: Optional[int] = None  # 1
    pageSize: Optional[int] = None  # 10

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcNewQuerySecurityGroupsResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpcNewQuerySecurityGroupsReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcNewQuerySecurityGroupsReturnObj:
    securityGroups: Optional[List['V4VpcNewQuerySecurityGroupsReturnObjSecurityGroups']] = None  # 安全组列表
    totalCount: Optional[int] = None  # 列表条目数
    currentCount: Optional[int] = None  # 分页查询时每页的行数。
    totalPage: Optional[int] = None  # 总页数


@dataclass_json
@dataclass
class V4VpcNewQuerySecurityGroupsReturnObjSecurityGroups:
    securityGroupName: Optional[str] = None  # 安全组名称
    id: Optional[str] = None  # 安全组id
    vmNum: Optional[int] = None  # 相关云主机
    origin: Optional[str] = None  # 表示是否是默认安全组
    vpcName: Optional[str] = None  # vpc名称
    vpcID: Optional[str] = None  # 安全组所属的专有网络。
    creationTime: Optional[str] = None  # 创建时间
    description: Optional[str] = None  # 安全组描述信息。
    projectID: Optional[str] = None  # 项目ID
    securityGroupRuleList: Optional[List['V4VpcNewQuerySecurityGroupsReturnObjSecurityGroupsSecurityGroupRuleList']] = None  # 安全组规则信息


@dataclass_json
@dataclass
class V4VpcNewQuerySecurityGroupsReturnObjSecurityGroupsSecurityGroupRuleList:
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
    action: Optional[str] = None  # 否
    origin: Optional[str] = None  # 类型
    remoteSecurityGroupID: Optional[str] = None  # 远端安全组id
    prefixListID: Optional[str] = None  # 前缀列表id
