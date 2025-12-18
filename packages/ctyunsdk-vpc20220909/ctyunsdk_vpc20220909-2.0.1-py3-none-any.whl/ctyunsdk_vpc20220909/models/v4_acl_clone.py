from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4AclCloneRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    destRegionID: str  # 目标资源池，仅支持从4.0资源池复制到4.0资源池
    srcAclID: str  # 源aclID
    vpcID: str  # 目标资源池得到的acl归属的vpc
    name: str  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4AclCloneResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4AclCloneReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4AclCloneReturnObj:
    aclID: Optional[str] = None  # acl id
    name: Optional[str] = None  # acl 名称
