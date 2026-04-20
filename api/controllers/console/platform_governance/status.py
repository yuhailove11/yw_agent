"""统一治理状态查询接口。"""

from flask_restx import Resource

from configs import dify_config
from controllers.console import console_ns
from controllers.console.wraps import account_initialization_required, setup_required
from libs.login import current_account_with_tenant, login_required
from services.platform_governance.client import platform_governance_client
from services.platform_governance.shadow_dataset_service import PlatformShadowDatasetService


@console_ns.route("/platform-governance/apps/<uuid:app_id>/status")
class PlatformGovernanceAppStatusApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    def get(self, app_id):
        _, current_tenant_id = current_account_with_tenant()
        resource_code = f"dify:app:{app_id}"
        if not dify_config.PLATFORM_GOVERNANCE_ENABLED:
            return {"enabled": False, "resource_code": resource_code}, 200
        payload = platform_governance_client.get_app_runtime_status(resource_code, current_tenant_id)
        payload["enabled"] = True
        return payload, 200


@console_ns.route("/platform-governance/knowledge-bases/selectable")
class PlatformGovernanceSelectableKnowledgeApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        _, current_tenant_id = current_account_with_tenant()
        if not dify_config.PLATFORM_GOVERNANCE_ENABLED:
            return {"enabled": False, "data": [], "total": 0}, 200
        payload = PlatformShadowDatasetService.sync_selectable_knowledge_bases(current_tenant_id)
        payload["enabled"] = True
        return payload, 200


@console_ns.route("/platform-governance/api-services/selectable")
class PlatformGovernanceSelectableApiServicesApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        _, current_tenant_id = current_account_with_tenant()
        if not dify_config.PLATFORM_GOVERNANCE_ENABLED:
            return {"enabled": False, "data": [], "total": 0}, 200
        payload = platform_governance_client.list_selectable_api_services(current_tenant_id)
        payload["enabled"] = True
        return payload, 200
