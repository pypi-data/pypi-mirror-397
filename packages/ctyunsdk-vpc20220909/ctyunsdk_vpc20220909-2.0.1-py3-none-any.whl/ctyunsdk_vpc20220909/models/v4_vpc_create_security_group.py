from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcCreateSecurityGroupRequest(CtyunOpenAPIRequest):
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池id
    vpcID: str  # 关联的vpcID
    name: str  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    projectID: Optional[str] = None  # 企业项目 ID，默认为0
    description: Optional[str] = None  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·~！@#￥%……&*（） —— -+={}|《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcCreateSecurityGroupResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpcCreateSecurityGroupReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcCreateSecurityGroupReturnObj:
    securityGroupID: Optional[str] = None  # sg-p2qs0qmigm
