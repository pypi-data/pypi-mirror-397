from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpcHavipBindRequest(CtyunOpenAPIRequest):
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池ID
    resourceType: str  # 绑定的实例类型，VM 表示虚拟机ECS, PM 表示裸金属, NETWORK 表示弹性 IP
    haVipID: str  # 高可用虚IP的ID
    networkInterfaceID: Optional[str] = None  # 虚拟网卡ID, 该网卡属于instanceID, 当 resourceType 为 VM / PM 时，必填
    instanceID: Optional[str] = None  # ECS示例ID，当 resourceType 为 VM / PM 时，必填
    floatingID: Optional[str] = None  # 弹性IP ID，当 resourceType 为 NETWORK 时，必填

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcHavipBindResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpcHavipBindReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpcHavipBindReturnObj:
    status: Optional[str] = None  # 绑定状态，取值 in_progress / done
    message: Optional[str] = None  # 绑定状态提示信息
