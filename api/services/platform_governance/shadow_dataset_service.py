"""统一平台注册中心知识库影子投影服务。"""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy import select

from extensions.ext_database import db
from models import Account, Dataset, DifyShadowDatasetBinding, ExternalKnowledgeApis, ExternalKnowledgeBindings
from models.account import TenantAccountJoin, TenantAccountRole
from models.dataset import DatasetPermissionEnum
from models.enums import DataSourceType
from services.platform_governance.client import platform_governance_client

logger = logging.getLogger(__name__)


class PlatformShadowDatasetService:
    SHARED_API_NAME = "统一知识库网关"
    SHARED_API_DESC = "由统一平台注册中心投影的已审批知识库"

    @staticmethod
    def _get_default_owner(tenant_id: str) -> Account | None:
        account_id = db.session.scalar(
            select(TenantAccountJoin.account_id)
            .where(
                TenantAccountJoin.tenant_id == tenant_id,
                TenantAccountJoin.role.in_([TenantAccountRole.OWNER, TenantAccountRole.ADMIN]),
            )
            .order_by(TenantAccountJoin.created_at.asc())
            .limit(1)
        )
        if account_id is None:
            return None
        return db.session.get(Account, account_id)

    @staticmethod
    def _ensure_shared_external_api(
        tenant_id: str,
        owner_id: str,
        endpoint: str,
        api_key: str,
    ) -> ExternalKnowledgeApis:
        entity = db.session.scalar(
            select(ExternalKnowledgeApis)
            .where(
                ExternalKnowledgeApis.tenant_id == tenant_id,
                ExternalKnowledgeApis.name == PlatformShadowDatasetService.SHARED_API_NAME,
            )
            .limit(1)
        )
        settings = {"endpoint": endpoint.rstrip("/"), "api_key": api_key}
        if entity is None:
            entity = ExternalKnowledgeApis(
                tenant_id=tenant_id,
                name=PlatformShadowDatasetService.SHARED_API_NAME,
                description=PlatformShadowDatasetService.SHARED_API_DESC,
                settings=json.dumps(settings, ensure_ascii=False),
                created_by=owner_id,
                updated_by=owner_id,
            )
            db.session.add(entity)
            db.session.flush()
            return entity
        entity.description = PlatformShadowDatasetService.SHARED_API_DESC
        entity.settings = json.dumps(settings, ensure_ascii=False)
        entity.updated_by = owner_id
        return entity

    @staticmethod
    def _build_dataset_name(item: dict[str, Any]) -> str:
        content = item.get("content") or {}
        name = str(item.get("name") or content.get("name") or item.get("resource_code") or "统一知识库")
        return f"[统一知识库] {name}"

    @staticmethod
    def _upsert_shadow_dataset(
        tenant_id: str,
        owner_id: str,
        external_api: ExternalKnowledgeApis,
        item: dict[str, Any],
    ) -> None:
        resource_code = str(item.get("resource_code") or "")
        content = item.get("content") or {}
        source_id = str(content.get("source_id") or content.get("knowledge_base_id") or "")
        binding = db.session.scalar(
            select(DifyShadowDatasetBinding)
            .where(
                DifyShadowDatasetBinding.tenant_id == tenant_id,
                DifyShadowDatasetBinding.resource_code == resource_code,
            )
            .limit(1)
        )

        dataset: Dataset | None = None
        if binding is not None:
            dataset = db.session.get(Dataset, binding.dataset_id)
        if dataset is None:
            dataset = Dataset(
                tenant_id=tenant_id,
                name=PlatformShadowDatasetService._build_dataset_name(item),
                description=str(content.get("summary") or item.get("name") or ""),
                provider="external",
                permission=DatasetPermissionEnum.ALL_TEAM,
                data_source_type=DataSourceType.UPLOAD_FILE,
                created_by=owner_id,
                updated_by=owner_id,
                retrieval_model={
                    "top_k": 4,
                    "score_threshold": 0.0,
                    "score_threshold_enabled": False,
                },
                enable_api=False,
            )
            db.session.add(dataset)
            db.session.flush()
            binding = DifyShadowDatasetBinding(
                dataset_id=dataset.id,
                tenant_id=tenant_id,
                resource_code=resource_code,
                source_system="ragflow",
            )
            db.session.add(binding)
        else:
            dataset.name = PlatformShadowDatasetService._build_dataset_name(item)
            dataset.description = str(content.get("summary") or item.get("name") or "")
            dataset.provider = "external"
            dataset.permission = DatasetPermissionEnum.ALL_TEAM
            dataset.updated_by = owner_id
            dataset.enable_api = False

        external_binding = db.session.scalar(
            select(ExternalKnowledgeBindings)
            .where(ExternalKnowledgeBindings.tenant_id == tenant_id, ExternalKnowledgeBindings.dataset_id == dataset.id)
            .limit(1)
        )
        external_knowledge_id = source_id or resource_code
        if external_binding is None:
            external_binding = ExternalKnowledgeBindings(
                tenant_id=tenant_id,
                external_knowledge_api_id=external_api.id,
                dataset_id=dataset.id,
                external_knowledge_id=external_knowledge_id,
                created_by=owner_id,
            )
            db.session.add(external_binding)
        else:
            external_binding.external_knowledge_api_id = external_api.id
            external_binding.external_knowledge_id = external_knowledge_id
            external_binding.updated_by = owner_id

    @staticmethod
    def sync_selectable_knowledge_bases(tenant_id: str) -> dict[str, Any]:
        if not platform_governance_client.enabled:
            return {"enabled": False, "data": [], "total": 0}
        owner = PlatformShadowDatasetService._get_default_owner(tenant_id)
        if owner is None:
            return {"enabled": True, "data": [], "total": 0}

        payload = platform_governance_client.list_selectable_knowledge_bases(tenant_id)
        items = payload.get("data") or []
        shadow_bindings = db.session.scalars(
            select(DifyShadowDatasetBinding).where(DifyShadowDatasetBinding.tenant_id == tenant_id)
        ).all()
        if not items:
            for shadow_binding in shadow_bindings:
                dataset = db.session.get(Dataset, shadow_binding.dataset_id)
                if dataset is None:
                    continue
                dataset.permission = DatasetPermissionEnum.PARTIAL_TEAM
                dataset.updated_by = owner.id
                dataset.enable_api = False
            db.session.commit()
            return {"enabled": True, "data": [], "total": 0}

        first_content = (items[0].get("content") or {}) if items else {}
        endpoint = str(first_content.get("retrieval_endpoint") or "").rstrip("/")
        api_key = str(first_content.get("retrieval_api_key") or "")
        if not endpoint or not api_key:
            logger.warning(
                "统一平台注册中心知识库缺少检索接入信息，无法投影为 Dify external dataset: tenant_id=%s",
                tenant_id,
            )
            return {"enabled": True, "data": items, "total": len(items)}

        external_api = PlatformShadowDatasetService._ensure_shared_external_api(tenant_id, owner.id, endpoint, api_key)
        published_resource_codes: set[str] = set()
        for item in items:
            resource_code = str(item.get("resource_code") or "")
            if not resource_code:
                continue
            published_resource_codes.add(resource_code)
            PlatformShadowDatasetService._upsert_shadow_dataset(tenant_id, owner.id, external_api, item)

        for shadow_binding in shadow_bindings:
            dataset = db.session.get(Dataset, shadow_binding.dataset_id)
            if dataset is None:
                continue
            if shadow_binding.resource_code not in published_resource_codes:
                dataset.permission = DatasetPermissionEnum.PARTIAL_TEAM
                dataset.enable_api = False
                dataset.updated_by = owner.id
            else:
                dataset.permission = DatasetPermissionEnum.ALL_TEAM
                dataset.enable_api = False
        db.session.commit()
        return {"enabled": True, "data": items, "total": len(items)}
