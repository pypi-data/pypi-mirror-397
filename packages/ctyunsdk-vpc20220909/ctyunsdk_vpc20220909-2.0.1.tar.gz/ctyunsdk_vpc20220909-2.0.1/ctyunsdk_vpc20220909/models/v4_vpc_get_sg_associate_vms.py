from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcGetSgAssociateVmsRequest(CtyunOpenAPIRequest):
    regionID: str  # 区域id
    securityGroupID: str  # 安全组ID
    projectID: Optional[str] = None  # 企业项目 ID，默认为0
    pageNo: Optional[int] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[int] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcGetSgAssociateVmsResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpcGetSgAssociateVmsReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcGetSgAssociateVmsReturnObj:
    results: Optional[List['V4VpcGetSgAssociateVmsReturnObjResults']] = None  # 业务数据
    totalCount: Optional[int] = None  # 列表条目数
    currentCount: Optional[int] = None  # 分页查询时每页的行数。
    totalPage: Optional[int] = None  # 总页数


@dataclass_json
@dataclass
class V4VpcGetSgAssociateVmsReturnObjResults:
    instanceID: Optional[str] = None  # 主机 ID
    instanceName: Optional[str] = None  # 主机名
    instanceType: Optional[str] = None  # 主机类型：VM / BM
    instanceState: Optional[str] = None  # 主机状态
    privateIp: Optional[str] = None  # 私有 ipv4
    privateIpv6: Optional[str] = None  # 私有 ipv6
