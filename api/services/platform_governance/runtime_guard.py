"""统一平台注册中心运行时治理校验。"""

from __future__ import annotations

from sqlalchemy import select

from configs import dify_config
from extensions.ext_database import db
from models.dataset import Dataset
from models.model import DifyShadowDatasetBinding
from services.platform_governance.client import platform_governance_client


class PlatformRuntimeGuard:
    @staticmethod
    def ensure_external_dataset_allowed(
        dataset: Dataset,
        user_id: str | None = None,
        consumer: str | None = None,
    ) -> None:
        if (
            not platform_governance_client.enabled
            or not dify_config.PLATFORM_ONLY_EXTERNAL_APPROVED_KNOWLEDGE
            or dataset.provider != "external"
        ):
            return
        shadow_binding = select(DifyShadowDatasetBinding).where(
            DifyShadowDatasetBinding.dataset_id == dataset.id,
            DifyShadowDatasetBinding.tenant_id == dataset.tenant_id,
        )
        binding = db.session.scalar(shadow_binding)
        if binding is None:
            raise ValueError("external dataset is not governed by unified platform")
        payload = platform_governance_client.get_resource_runtime_status(
            binding.resource_code,
            dataset.tenant_id,
            user_id=user_id,
            consumer=consumer,
        )
        if not payload.get("allowed"):
            raise ValueError(f"external dataset blocked by platform governance: {payload.get('reason', 'denied')}")
