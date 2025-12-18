from ctyun_python_sdk_core import CtyunClient, Credential, ClientConfig, CtyunRequestException

from .models import *


class VpcClient:
    def __init__(self, client_config: ClientConfig):
        self.endpoint = client_config.endpoint
        self.credential = Credential(client_config.access_key_id, client_config.access_key_secret)
        self.ctyun_client = CtyunClient(client_config.verify_tls)

    def v4_acl_rule_list(self, request: V4AclRuleListRequest) -> V4AclRuleListResponse:
        """查看 Acl 规则列表"""
        url = f"{self.endpoint}/v4/acl-rule/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4AclRuleListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_acl_rule_update(self, request: V4AclRuleUpdateRequest) -> V4AclRuleUpdateResponse:
        """修改 Acl 规则列表属性"""
        url = f"{self.endpoint}/v4/acl-rule/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4AclRuleUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_acl_rule_delete(self, request: V4AclRuleDeleteRequest) -> V4AclRuleDeleteResponse:
        """删除 Acl 规则列表"""
        url = f"{self.endpoint}/v4/acl-rule/delete"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4AclRuleDeleteResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_acl_rule_create(self, request: V4AclRuleCreateRequest) -> V4AclRuleCreateResponse:
        """创建 Acl 规则"""
        url = f"{self.endpoint}/v4/acl-rule/create"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4AclRuleCreateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_delete(self, request: V4VpcRouteTableDeleteRequest) -> V4VpcRouteTableDeleteResponse:
        """删除路由表，其中自定义路由表可以删除，默认路由表随 VPC 删除时一起删除。"""
        url = f"{self.endpoint}/v4/vpc/route-table/delete"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableDeleteResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_create_rules(self, request: V4VpcRouteTableCreateRulesRequest) -> V4VpcRouteTableCreateRulesResponse:
        """创建路由表规则"""
        url = f"{self.endpoint}/v4/vpc/route-table/create-rules"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableCreateRulesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_modify(self, request: V4VpcRouteTableModifyRequest) -> V4VpcRouteTableModifyResponse:
        """修改路由表属性"""
        url = f"{self.endpoint}/v4/vpc/route-table/modify"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableModifyResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_create_rule(self, request: V4VpcRouteTableCreateRuleRequest) -> V4VpcRouteTableCreateRuleResponse:
        """创建单条路由规则"""
        url = f"{self.endpoint}/v4/vpc/route-table/create-rule"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableCreateRuleResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_delete_rule(self, request: V4VpcRouteTableDeleteRuleRequest) -> V4VpcRouteTableDeleteRuleResponse:
        """修改路由表规则"""
        url = f"{self.endpoint}/v4/vpc/route-table/delete-rule"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableDeleteRuleResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_create(self, request: V4VpcRouteTableCreateRequest) -> V4VpcRouteTableCreateResponse:
        """创建路由表"""
        url = f"{self.endpoint}/v4/vpc/route-table/create"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableCreateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_create_gateway_routetable(self, request: V4VpcRouteTableCreateGatewayRoutetableRequest) -> V4VpcRouteTableCreateGatewayRoutetableResponse:
        """创建网关路由表"""
        url = f"{self.endpoint}/v4/vpc/route-table/create-gateway-routetable"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableCreateGatewayRoutetableResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_show(self, request: V4VpcRouteTableShowRequest) -> V4VpcRouteTableShowResponse:
        """查询路由表详情"""
        url = f"{self.endpoint}/v4/vpc/route-table/show"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableShowResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_list_rules(self, request: V4VpcRouteTableListRulesRequest) -> V4VpcRouteTableListRulesResponse:
        """查询路由表规则列表"""
        url = f"{self.endpoint}/v4/vpc/route-table/list-rules"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableListRulesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_modify_rule(self, request: V4VpcRouteTableModifyRuleRequest) -> V4VpcRouteTableModifyRuleResponse:
        """修改单条路由表规则"""
        url = f"{self.endpoint}/v4/vpc/route-table/modify-rule"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableModifyRuleResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_new_list_rules(self, request: V4VpcRouteTableNewListRulesRequest) -> V4VpcRouteTableNewListRulesResponse:
        """查询路由表规则列表"""
        url = f"{self.endpoint}/v4/vpc/route-table/new-list-rules"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableNewListRulesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_list(self, request: V4VpcRouteTableListRequest) -> V4VpcRouteTableListResponse:
        """查询路由表列表"""
        url = f"{self.endpoint}/v4/vpc/route-table/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_new_list(self, request: V4VpcRouteTableNewListRequest) -> V4VpcRouteTableNewListResponse:
        """查询路由表列表"""
        url = f"{self.endpoint}/v4/vpc/route-table/new-list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableNewListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_delete_rules(self, request: V4VpcRouteTableDeleteRulesRequest) -> V4VpcRouteTableDeleteRulesResponse:
        """删除路由表规则"""
        url = f"{self.endpoint}/v4/vpc/route-table/delete-rules"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableDeleteRulesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_route_table_modify_rules(self, request: V4VpcRouteTableModifyRulesRequest) -> V4VpcRouteTableModifyRulesResponse:
        """修改路由表规则"""
        url = f"{self.endpoint}/v4/vpc/route-table/modify-rules"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRouteTableModifyRulesResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_acl_new_list(self, request: V4AclNewListRequest) -> V4AclNewListResponse:
        """查看 Acl 列表信息"""
        url = f"{self.endpoint}/v4/acl/new-list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4AclNewListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_acl_query(self, request: V4AclQueryRequest) -> V4AclQueryResponse:
        """查看 Acl 的详细信息"""
        url = f"{self.endpoint}/v4/acl/query"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4AclQueryResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_acl_create(self, request: V4AclCreateRequest) -> V4AclCreateResponse:
        """创建 Acl"""
        url = f"{self.endpoint}/v4/acl/create"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4AclCreateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_acl_clone(self, request: V4AclCloneRequest) -> V4AclCloneResponse:
        """克隆 Acl,仅实现acl的规则复制，不包括关联资源和相关属性"""
        url = f"{self.endpoint}/v4/acl/clone"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4AclCloneResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_acl_delete(self, request: V4AclDeleteRequest) -> V4AclDeleteResponse:
        """删除 Acl"""
        url = f"{self.endpoint}/v4/acl/delete"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4AclDeleteResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_acl_list(self, request: V4AclListRequest) -> V4AclListResponse:
        """查看 Acl 列表信息"""
        url = f"{self.endpoint}/v4/acl/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4AclListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def openapi_v4_acl_update(self, request: OpenapiV4AclUpdateRequest) -> OpenapiV4AclUpdateResponse:
        """修改 Acl 属性"""
        url = f"{self.endpoint}/v4/acl/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, OpenapiV4AclUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_delete_subnet(self, request: V4VpcDeleteSubnetRequest) -> V4VpcDeleteSubnetResponse:
        """删除子网"""
        url = f"{self.endpoint}/v4/vpc/delete-subnet"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcDeleteSubnetResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_disassociate_subnet_acl(self, request: V4VpcDisassociateSubnetAclRequest) -> V4VpcDisassociateSubnetAclResponse:
        """子网解绑 ACL"""
        url = f"{self.endpoint}/v4/vpc/disassociate-subnet-acl"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcDisassociateSubnetAclResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_replace_subnet_route_table(self, request: V4VpcReplaceSubnetRouteTableRequest) -> V4VpcReplaceSubnetRouteTableResponse:
        """子网更换路由表，子网必须关联一张路由表。创建VPC后会自动生成一张默认路由表，新建子网时，会关联到默认路由表，子网可以更换其他路由表。"""
        url = f"{self.endpoint}/v4/vpc/replace-subnet-route-table"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcReplaceSubnetRouteTableResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_update_subnet(self, request: V4VpcUpdateSubnetRequest) -> V4VpcUpdateSubnetResponse:
        """修改子网的属性：名称、描述。"""
        url = f"{self.endpoint}/v4/vpc/update-subnet"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcUpdateSubnetResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_associate_secondary_cidrs(self, request: V4VpcAssociateSecondaryCidrsRequest) -> V4VpcAssociateSecondaryCidrsResponse:
        """VPC 绑定扩展网段"""
        url = f"{self.endpoint}/v4/vpc/associate-secondary-cidrs"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcAssociateSecondaryCidrsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_query_subnet(self, request: V4VpcQuerySubnetRequest) -> V4VpcQuerySubnetResponse:
        """查询用户专有网络 VPC 下子网详情。"""
        url = f"{self.endpoint}/v4/vpc/query-subnet"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcQuerySubnetResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_update_ipv6_status(self, request: V4VpcUpdateIpv6StatusRequest) -> V4VpcUpdateIpv6StatusResponse:
        """修改专有网络VPC的 IPv6 状态：开启、关闭。关闭VPC的IPv6开关前，需要关闭所有子网的IPv6开关。"""
        url = f"{self.endpoint}/v4/vpc/update-ipv6-status"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcUpdateIpv6StatusResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_replace_subnet_acl(self, request: V4VpcReplaceSubnetAclRequest) -> V4VpcReplaceSubnetAclResponse:
        """子网替换 ACL"""
        url = f"{self.endpoint}/v4/vpc/replace-subnet-acl"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcReplaceSubnetAclResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_list_subnet(self, request: V4VpcListSubnetRequest) -> V4VpcListSubnetResponse:
        """查询用户专有网络下子网列表"""
        url = f"{self.endpoint}/v4/vpc/list-subnet"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcListSubnetResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_create_subnet(self, request: V4VpcCreateSubnetRequest) -> V4VpcCreateSubnetResponse:
        """创建子网。"""
        url = f"{self.endpoint}/v4/vpc/create-subnet"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcCreateSubnetResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_list(self, request: V4VpcListRequest) -> V4VpcListResponse:
        """查询用户专有网络列表"""
        url = f"{self.endpoint}/v4/vpc/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_new_list(self, request: V4VpcNewListRequest) -> V4VpcNewListResponse:
        """查询用户专有网络列表"""
        url = f"{self.endpoint}/v4/vpc/new-list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcNewListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_update_subnet_ipv6_status(self, request: V4VpcUpdateSubnetIpv6StatusRequest) -> V4VpcUpdateSubnetIpv6StatusResponse:
        """修改子网subnet的 IPv6 状态：开启、关闭。开启子网IPv6前，需要先开启VPC的IPv6。关闭子网IPv6前，需要删除所有占用IPv6地址的实例。"""
        url = f"{self.endpoint}/v4/vpc/update-subnet-ipv6-status"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcUpdateSubnetIpv6StatusResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_disassociate_secondary_cidrs(self, request: V4VpcDisassociateSecondaryCidrsRequest) -> V4VpcDisassociateSecondaryCidrsResponse:
        """VPC解绑扩展网段。"""
        url = f"{self.endpoint}/v4/vpc/disassociate-secondary-cidrs"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcDisassociateSecondaryCidrsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_new_list_subnet(self, request: V4VpcNewListSubnetRequest) -> V4VpcNewListSubnetResponse:
        """查询用户专有网络下子网列表"""
        url = f"{self.endpoint}/v4/vpc/new-list-subnet"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcNewListSubnetResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_query(self, request: V4VpcQueryRequest) -> V4VpcQueryResponse:
        """查询用户专有网络"""
        url = f"{self.endpoint}/v4/vpc/query"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcQueryResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_delete(self, request: V4VpcDeleteRequest) -> V4VpcDeleteResponse:
        """
        删除专有网络
        删除专有网络之前，需要先删除所有子网，且需要删除子网内所有的云资源，包括ECS、弹性裸金属服务器、弹性负载均衡、NAT网关、高可用虚拟 IP 等，需要将子网内的占用IP的资源全部释放。
        """
        url = f"{self.endpoint}/v4/vpc/delete"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcDeleteResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_update(self, request: V4VpcUpdateRequest) -> V4VpcUpdateResponse:
        """修改专有网络VPC的属性：名称、描述。"""
        url = f"{self.endpoint}/v4/vpc/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_list_used_ips(self, request: V4VpcListUsedIpsRequest) -> V4VpcListUsedIpsResponse:
        """查看某个子网已使用IP"""
        url = f"{self.endpoint}/v4/vpc/list-used-ips"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcListUsedIpsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_detach(self, request: V4PortsDetachRequest) -> V4PortsDetachResponse:
        """网卡解绑实例"""
        url = f"{self.endpoint}/v4/ports/detach"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsDetachResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_new_list(self, request: V4PortsNewListRequest) -> V4PortsNewListResponse:
        """弹性网卡列表"""
        url = f"{self.endpoint}/v4/ports/new-list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4PortsNewListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_check_status(self, request: V4PortsCheckStatusRequest) -> V4PortsCheckStatusResponse:
        """获取网卡状态接口"""
        url = f"{self.endpoint}/v4/ports/check-status"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4PortsCheckStatusResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_unassign_ipv6(self, request: V4PortsUnassignIpv6Request) -> V4PortsUnassignIpv6Response:
        """单个网卡解绑多个 IPv6 地址"""
        url = f"{self.endpoint}/v4/ports/unassign-ipv6"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsUnassignIpv6Response)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_unassign_secondary_private_ips(self, request: V4PortsUnassignSecondaryPrivateIpsRequest) -> V4PortsUnassignSecondaryPrivateIpsResponse:
        """网卡解绑辅助私网IP"""
        url = f"{self.endpoint}/v4/ports/unassign-secondary-private-ips"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsUnassignSecondaryPrivateIpsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_change_private_ip(self, request: V4PortsChangePrivateIpRequest) -> V4PortsChangePrivateIpResponse:
        """修改内网IP"""
        url = f"{self.endpoint}/v4/ports/change-private-ip"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsChangePrivateIpResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_change_vpc(self, request: V4PortsChangeVpcRequest) -> V4PortsChangeVpcResponse:
        """更换VPC"""
        url = f"{self.endpoint}/v4/ports/change-vpc"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsChangeVpcResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_assign_ipv6(self, request: V4PortsAssignIpv6Request) -> V4PortsAssignIpv6Response:
        """单个网卡关联多个IPv6地址"""
        url = f"{self.endpoint}/v4/ports/assign-ipv6"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsAssignIpv6Response)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_assign_secondary_private_ips(self, request: V4PortsAssignSecondaryPrivateIpsRequest) -> V4PortsAssignSecondaryPrivateIpsResponse:
        """网卡关联辅助私网IP"""
        url = f"{self.endpoint}/v4/ports/assign-secondary-private-ips"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsAssignSecondaryPrivateIpsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_batch_assign_ipv6(self, request: V4PortsBatchAssignIpv6Request) -> V4PortsBatchAssignIpv6Response:
        """多个网卡关联IPv6（批量使用）"""
        url = f"{self.endpoint}/v4/ports/batch-assign-ipv6"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsBatchAssignIpv6Response)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_update(self, request: V4PortsUpdateRequest) -> V4PortsUpdateResponse:
        """修改网卡属性"""
        url = f"{self.endpoint}/v4/ports/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_async_detach_bm(self, request: V4PortsAsyncDetachBmRequest) -> V4PortsAsyncDetachBmResponse:
        """网卡解绑物理机"""
        url = f"{self.endpoint}/v4/ports/async-detach-bm"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsAsyncDetachBmResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_create(self, request: V4PortsCreateRequest) -> V4PortsCreateResponse:
        """创建弹性网卡"""
        url = f"{self.endpoint}/v4/ports/create"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsCreateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_check_status_batch(self, request: V4PortsCheckStatusBatchRequest) -> V4PortsCheckStatusBatchResponse:
        """网卡状态批量查询接口"""
        url = f"{self.endpoint}/v4/ports/check-status-batch"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4PortsCheckStatusBatchResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_attach(self, request: V4PortsAttachRequest) -> V4PortsAttachResponse:
        """网卡绑定实例"""
        url = f"{self.endpoint}/v4/ports/attach"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsAttachResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_show(self, request: V4PortsShowRequest) -> V4PortsShowResponse:
        """查询网卡信息"""
        url = f"{self.endpoint}/v4/ports/show"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4PortsShowResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_async_attach_bm(self, request: V4PortsAsyncAttachBmRequest) -> V4PortsAsyncAttachBmResponse:
        """网卡绑定物理机"""
        url = f"{self.endpoint}/v4/ports/async-attach-bm"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsAsyncAttachBmResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_batch_unassign_ipv6(self, request: V4PortsBatchUnassignIpv6Request) -> V4PortsBatchUnassignIpv6Response:
        """多个网卡解绑IPv6地址（批量使用）"""
        url = f"{self.endpoint}/v4/ports/batch-unassign-ipv6"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsBatchUnassignIpv6Response)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_delete(self, request: V4PortsDeleteRequest) -> V4PortsDeleteResponse:
        """删除弹性网卡"""
        url = f"{self.endpoint}/v4/ports/delete"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4PortsDeleteResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_ports_list(self, request: V4PortsListRequest) -> V4PortsListResponse:
        """弹性网卡列表"""
        url = f"{self.endpoint}/v4/ports/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4PortsListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_havip_show(self, request: V4VpcHavipShowRequest) -> V4VpcHavipShowResponse:
        """查看高可用虚 IP 详情"""
        url = f"{self.endpoint}/v4/vpc/havip/show"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcHavipShowResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_havip_unbind(self, request: V4VpcHavipUnbindRequest) -> V4VpcHavipUnbindResponse:
        """将 HaVip 从 ECS 实例上解绑，由于绑定是异步操作，在第一次请求后，并不会立即返回解绑结果，调用者在获取到解绑状态为 in\_progress 时，继续使用相同参数进行请求，获取最新的解绑结果，直到最后的解绑状态为 done 即可停止请求。"""
        url = f"{self.endpoint}/v4/vpc/havip/unbind"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcHavipUnbindResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_havip_delete(self, request: V4VpcHavipDeleteRequest) -> V4VpcHavipDeleteResponse:
        """删除高可用虚IP"""
        url = f"{self.endpoint}/v4/vpc/havip/delete"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcHavipDeleteResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_havip_list(self, request: V4VpcHavipListRequest) -> V4VpcHavipListResponse:
        """查询高可用虚IP列表"""
        url = f"{self.endpoint}/v4/vpc/havip/list"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcHavipListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_havip_bind(self, request: V4VpcHavipBindRequest) -> V4VpcHavipBindResponse:
        """将HaVip绑定到ECS实例上，由于绑定是异步操作，在第一次请求后，并不会立即返回绑定结果，调用者在获取到绑定状态为 in\_progress 时，继续使用相同参数进行请求，获取最新的绑定结果，直到最后的绑定状态为 done 即可停止请求。"""
        url = f"{self.endpoint}/v4/vpc/havip/bind"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcHavipBindResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_modify_security_group_egress(self, request: V4VpcModifySecurityGroupEgressRequest) -> V4VpcModifySecurityGroupEgressResponse:
        """修改安全组出方向规则的描述信息。该接口只能修改出方向描述信息。如果您需要修改安全组规则的策略、端口范围等信息，请在管理控制台修改。"""
        url = f"{self.endpoint}/v4/vpc/modify-security-group-egress"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcModifySecurityGroupEgressResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_join_security_group(self, request: V4VpcJoinSecurityGroupRequest) -> V4VpcJoinSecurityGroupResponse:
        """解绑安全组。"""
        url = f"{self.endpoint}/v4/vpc/join-security-group"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcJoinSecurityGroupResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_batch_attach_security_group_ports(self, request: V4VpcBatchAttachSecurityGroupPortsRequest) -> V4VpcBatchAttachSecurityGroupPortsResponse:
        """安全组批量绑定网卡。"""
        url = f"{self.endpoint}/v4/vpc/batch-attach-security-group-ports"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcBatchAttachSecurityGroupPortsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_describe_security_group_rule(self, request: V4VpcDescribeSecurityGroupRuleRequest) -> V4VpcDescribeSecurityGroupRuleResponse:
        """安全组规则详情。"""
        url = f"{self.endpoint}/v4/vpc/describe-security-group-rule"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcDescribeSecurityGroupRuleResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_modify_security_group_ingress(self, request: V4VpcModifySecurityGroupIngressRequest) -> V4VpcModifySecurityGroupIngressResponse:
        """修改安全组入方向规则的描述信息。该接口只能修改入方向描述信息。如果您需要修改安全组规则的策略、端口范围等信息，请在管理控制台修改。"""
        url = f"{self.endpoint}/v4/vpc/modify-security-group-ingress"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcModifySecurityGroupIngressResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_batch_join_security_group(self, request: V4VpcBatchJoinSecurityGroupRequest) -> V4VpcBatchJoinSecurityGroupResponse:
        """批量绑定安全组。"""
        url = f"{self.endpoint}/v4/vpc/batch-join-security-group"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcBatchJoinSecurityGroupResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_modify_security_group_attribute(self, request: V4VpcModifySecurityGroupAttributeRequest) -> V4VpcModifySecurityGroupAttributeResponse:
        """更新安全组。"""
        url = f"{self.endpoint}/v4/vpc/modify-security-group-attribute"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcModifySecurityGroupAttributeResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_pre_check_sg_rule(self, request: V4VpcPreCheckSgRuleRequest) -> V4VpcPreCheckSgRuleResponse:
        """安全组规则检查"""
        url = f"{self.endpoint}/v4/vpc/pre-check-sg-rule"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcPreCheckSgRuleResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_leave_security_group(self, request: V4VpcLeaveSecurityGroupRequest) -> V4VpcLeaveSecurityGroupResponse:
        """解绑安全组。"""
        url = f"{self.endpoint}/v4/vpc/leave-security-group"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcLeaveSecurityGroupResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_create_security_group_egress(self, request: V4VpcCreateSecurityGroupEgressRequest) -> V4VpcCreateSecurityGroupEgressResponse:
        """创建安全组出向规则。"""
        url = f"{self.endpoint}/v4/vpc/create-security-group-egress"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcCreateSecurityGroupEgressResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_get_sg_associate_vms(self, request: V4VpcGetSgAssociateVmsRequest) -> V4VpcGetSgAssociateVmsResponse:
        """获取安全组绑定机器列表"""
        url = f"{self.endpoint}/v4/vpc/get-sg-associate-vms"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcGetSgAssociateVmsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_query_security_groups(self, request: V4VpcQuerySecurityGroupsRequest) -> V4VpcQuerySecurityGroupsResponse:
        """查询用户安全组列表。"""
        url = f"{self.endpoint}/v4/vpc/query-security-groups"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcQuerySecurityGroupsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_delete_security_group(self, request: V4VpcDeleteSecurityGroupRequest) -> V4VpcDeleteSecurityGroupResponse:
        """删除安全组。删除安全组之前，请确保安全组内不存在实例。"""
        url = f"{self.endpoint}/v4/vpc/delete-security-group"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcDeleteSecurityGroupResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_batch_detach_security_group_ports(self, request: V4VpcBatchDetachSecurityGroupPortsRequest) -> V4VpcBatchDetachSecurityGroupPortsResponse:
        """安全组批量解绑网卡。"""
        url = f"{self.endpoint}/v4/vpc/batch-detach-security-group-ports"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcBatchDetachSecurityGroupPortsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_revoke_security_group_egress(self, request: V4VpcRevokeSecurityGroupEgressRequest) -> V4VpcRevokeSecurityGroupEgressResponse:
        """删除一条出方向安全组规则，撤销安全组出方向的权限设置。"""
        url = f"{self.endpoint}/v4/vpc/revoke-security-group-egress"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRevokeSecurityGroupEgressResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_new_query_security_groups(self, request: V4VpcNewQuerySecurityGroupsRequest) -> V4VpcNewQuerySecurityGroupsResponse:
        """查询用户安全组列表。"""
        url = f"{self.endpoint}/v4/vpc/new-query-security-groups"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcNewQuerySecurityGroupsResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_revoke_security_group_ingress(self, request: V4VpcRevokeSecurityGroupIngressRequest) -> V4VpcRevokeSecurityGroupIngressResponse:
        """删除一条入方向安全组规则，撤销安全组出方向的权限设置。"""
        url = f"{self.endpoint}/v4/vpc/revoke-security-group-ingress"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcRevokeSecurityGroupIngressResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_create_security_group_ingress(self, request: V4VpcCreateSecurityGroupIngressRequest) -> V4VpcCreateSecurityGroupIngressResponse:
        """创建安全组入向规则。"""
        url = f"{self.endpoint}/v4/vpc/create-security-group-ingress"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcCreateSecurityGroupIngressResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_describe_security_group_attribute(self, request: V4VpcDescribeSecurityGroupAttributeRequest) -> V4VpcDescribeSecurityGroupAttributeResponse:
        """查询用户安全组详情。"""
        url = f"{self.endpoint}/v4/vpc/describe-security-group-attribute"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpcDescribeSecurityGroupAttributeResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_create_security_group(self, request: V4VpcCreateSecurityGroupRequest) -> V4VpcCreateSecurityGroupResponse:
        """创建安全组。"""
        url = f"{self.endpoint}/v4/vpc/create-security-group"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcCreateSecurityGroupResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_ipv4_gw_add_route_table_binding(self, request: V4VpcIpv4GwAddRouteTableBindingRequest) -> V4VpcIpv4GwAddRouteTableBindingResponse:
        """IPv4网关绑定网关路由表"""
        url = f"{self.endpoint}/v4/vpc/ipv4-gw/add-route-table-binding"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcIpv4GwAddRouteTableBindingResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def vpc_create(self, request: VpcCreateRequest) -> VpcCreateResponse:
        """创建一个专有网络VPC。"""
        url = f"{self.endpoint}/v4/vpc/create"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, VpcCreateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_havip_create(self, request: V4VpcHavipCreateRequest) -> V4VpcHavipCreateResponse:
        """创建高可用虚IP"""
        url = f"{self.endpoint}/v4/vpc/havip/create"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcHavipCreateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpc_ipv4_gw_remove_route_table_binding(self, request: V4VpcIpv4GwRemoveRouteTableBindingRequest) -> V4VpcIpv4GwRemoveRouteTableBindingResponse:
        """IPv4网关解绑网关路由表"""
        url = f"{self.endpoint}/v4/vpc/ipv4-gw/remove-route-table-binding"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpcIpv4GwRemoveRouteTableBindingResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))



