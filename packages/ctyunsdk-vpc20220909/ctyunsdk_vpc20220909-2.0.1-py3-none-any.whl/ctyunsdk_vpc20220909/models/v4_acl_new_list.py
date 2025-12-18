from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4AclNewListRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    aclID: Optional[str] = None  # aclID
    name: Optional[str] = None  # acl Name
    pageNumber: Optional[int] = None  # 列表的页码，默认值为1
    pageNo: Optional[int] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[int] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4AclNewListResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4AclNewListReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4AclNewListReturnObj:
    acls: Optional[List['V4AclNewListReturnObjAcls']] = None  # acl 规则列表
    totalCount: Optional[int] = None  # 列表条目数。
    currentCount: Optional[int] = None  # 分页查询时每页的行数。
    totalPage: Optional[int] = None  # 分页查询时总页数。


@dataclass_json
@dataclass
class V4AclNewListReturnObjAcls:
    aclID: Optional[str] = None  # acl id
    name: Optional[str] = None  # acl 名称
    description: Optional[str] = None  # 描述
    applyToPublicLb: Optional[bool] = None  # 是否启用acl管控lb流量
    vpcID: Optional[str] = None  # 虚拟私有云 id
    enabled: Optional[str] = None  # 是否启用，取值范围：disable,enable
    inPolicyID: Optional[List[str]] = None  # 入规则id数组
    outPolicyID: Optional[List[str]] = None  # 出规则id数组
    createdAt: Optional[str] = None  # 创建时间
    updatedAt: Optional[str] = None  # 更新时间
    subnetIDs: Optional[List[str]] = None  # acl 绑定的子网 id
