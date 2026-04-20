"""Dify 资源同步服务。"""

from __future__ import annotations

import json
import logging

from models import App
from extensions.ext_database import db
from models.model import AppModelConfig, DifyRegistryAppBinding, DifySyncOutbox
from services.platform_governance.client import platform_governance_client

logger = logging.getLogger(__name__)


class PlatformGovernanceSyncService:
    @staticmethod
    def _build_payload(app: App, app_model_config: AppModelConfig | None = None) -> dict:
        return {
            "source_id": app.id,
            "workspace_id": app.tenant_id,
            "owner_user_id": app.created_by,
            "name": app.name,
            "summary": app.description or app.name,
            "version_label": f"app-{app.updated_at.isoformat() if app.updated_at else 'v1'}",
            "app_id": app.id,
            "app_mode": str(app.mode),
            "enable_api": app.enable_api,
            "enable_site": app.enable_site,
            "workflow_id": app.workflow_id,
            "model_config": app_model_config.to_dict() if app_model_config else (app.app_model_config.to_dict() if app.app_model_config else None),
        }

    @staticmethod
    def _upsert_binding(app: App, payload: dict, sync_status: str) -> None:
        resource_code = f"dify:app:{app.id}"
        binding = db.session.query(DifyRegistryAppBinding).filter_by(app_id=app.id).first()
        if binding is None:
            binding = DifyRegistryAppBinding(
                app_id=app.id,
                tenant_id=app.tenant_id,
                resource_code=resource_code,
                sync_status=sync_status,
                last_payload=json.dumps(payload, ensure_ascii=False),
            )
            db.session.add(binding)
        else:
            binding.tenant_id = app.tenant_id
            binding.resource_code = resource_code
            binding.sync_status = sync_status
            binding.last_payload = json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def _append_outbox(app: App, operation: str, payload: dict, status: str, error_message: str | None = None) -> None:
        db.session.add(
            DifySyncOutbox(
                tenant_id=app.tenant_id,
                resource_type="app",
                resource_id=app.id,
                operation=operation,
                payload=json.dumps(payload, ensure_ascii=False),
                status=status,
                error_message=error_message,
            )
        )

    @staticmethod
    def sync_app(app: App, app_model_config: AppModelConfig | None = None) -> None:
        if not platform_governance_client.enabled:
            return
        payload = PlatformGovernanceSyncService._build_payload(app, app_model_config)
        try:
            platform_governance_client.sync_app(payload)
            PlatformGovernanceSyncService._upsert_binding(app, payload, "synced")
            PlatformGovernanceSyncService._append_outbox(app, "upsert", payload, "success")
            db.session.commit()
        except Exception:
            db.session.rollback()
            try:
                PlatformGovernanceSyncService._upsert_binding(app, payload, "failed")
                PlatformGovernanceSyncService._append_outbox(app, "upsert", payload, "failed", "sync_app_failed")
                db.session.commit()
            except Exception:
                db.session.rollback()
            logger.exception("同步 Dify 应用失败: app_id=%s", app.id)

    @staticmethod
    def delete_app(app_id: str) -> None:
        if not platform_governance_client.enabled:
            return
        binding = db.session.query(DifyRegistryAppBinding).filter_by(app_id=app_id).first()
        tenant_id = binding.tenant_id if binding else ""
        payload = {"app_id": app_id, "resource_code": f"dify:app:{app_id}"}
        try:
            platform_governance_client.delete_app(app_id)
            if binding is not None:
                binding.sync_status = "deleted"
                binding.last_payload = json.dumps(payload, ensure_ascii=False)
            if tenant_id:
                db.session.add(
                    DifySyncOutbox(
                        tenant_id=tenant_id,
                        resource_type="app",
                        resource_id=app_id,
                        operation="delete",
                        payload=json.dumps(payload, ensure_ascii=False),
                        status="success",
                    )
                )
            db.session.commit()
        except Exception:
            db.session.rollback()
            try:
                if binding is not None:
                    binding.sync_status = "failed"
                    binding.last_payload = json.dumps(payload, ensure_ascii=False)
                if tenant_id:
                    db.session.add(
                        DifySyncOutbox(
                            tenant_id=tenant_id,
                            resource_type="app",
                            resource_id=app_id,
                            operation="delete",
                            payload=json.dumps(payload, ensure_ascii=False),
                            status="failed",
                            error_message="delete_app_failed",
                        )
                    )
                db.session.commit()
            except Exception:
                db.session.rollback()
            logger.exception("删除 Dify 应用映射失败: app_id=%s", app_id)
