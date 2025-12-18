from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcNewListRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池 ID
    vpcID: Optional[str] = None  # 多个 VPC 的 ID 之间用半角逗号（,）隔开。
    vpcName: Optional[str] = None  # vpc 名字
    pageNumber: Optional[int] = None  # 列表的页码，默认值为 1。
    pageNo: Optional[int] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[int] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10。
    projectID: Optional[str] = None  # 企业项目 ID，默认为0

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcNewListResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpcNewListReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcNewListReturnObj:
    vpcs: Optional[List['V4VpcNewListReturnObjVpcs']] = None  # vpc 组
    totalCount: Optional[int] = None  # 列表条目数
    currentCount: Optional[int] = None  # 分页查询时每页的行数。
    totalPage: Optional[int] = None  # 总页数


@dataclass_json
@dataclass
class V4VpcNewListReturnObjVpcs:
    vpcID: Optional[str] = None  # vpc 示例 ID
    name: Optional[str] = None  # 名称
    description: Optional[str] = None  # 描述
    CIDR: Optional[str] = None  # 子网
    ipv6Enabled: Optional[bool] = None  # 是否开启 ipv6
    enableIpv6: Optional[bool] = None  # 是否开启 ipv6
    ipv6CIDRS: Optional[List[str]] = None  # ipv6 子网列表
    subnetIDs: Optional[List[str]] = None  # 子网 id 列表
    natGatewayIDs: Optional[List[str]] = None  # 网关 id 列表
    secondaryCIDRS: Optional[List[str]] = None  # 附加网段
    projectID: Optional[str] = None  # 企业项目 ID，默认为0
    ipv6Infos: Optional[List[object]] = None  # vpc ipv6网段列表
