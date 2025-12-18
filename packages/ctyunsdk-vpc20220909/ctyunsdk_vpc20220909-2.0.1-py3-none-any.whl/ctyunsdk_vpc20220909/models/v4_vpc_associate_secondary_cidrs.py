from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcAssociateSecondaryCidrsRequest(CtyunOpenAPIRequest):
    clientToken: str  # 客户端存根，用于保证订单幂等性， 长度 1 - 64
    regionID: str  # 资源池ID
    vpcID: str  # vpc id
    cidrs: List[str]  # 是Array类型，里面的内容是String，要绑定的扩展网段ip，推荐192.168.0.0/16、172.16.0.0/12、10.0.0.0/8及其子网作为扩展网段，不能使用预占网段
    projectID: Optional[str] = None  # 企业项目 ID，默认为0

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcAssociateSecondaryCidrsResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


