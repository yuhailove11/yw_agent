"""应用变更后同步统一注册中心。"""

from events.app_event import (
    app_model_config_was_updated,
    app_published_workflow_was_updated,
    app_was_created,
    app_was_deleted,
    app_was_updated,
)
from services.platform_governance.sync_service import PlatformGovernanceSyncService


@app_was_created.connect
def handle_app_created(sender, **kwargs):
    PlatformGovernanceSyncService.sync_app(sender)


@app_was_updated.connect
def handle_app_updated(sender, **kwargs):
    PlatformGovernanceSyncService.sync_app(sender)


@app_model_config_was_updated.connect
def handle_app_model_config_updated(sender, **kwargs):
    PlatformGovernanceSyncService.sync_app(sender, kwargs.get("app_model_config"))


@app_published_workflow_was_updated.connect
def handle_app_published_workflow_updated(sender, **kwargs):
    PlatformGovernanceSyncService.sync_app(sender)


@app_was_deleted.connect
def handle_app_deleted(sender, **kwargs):
    PlatformGovernanceSyncService.delete_app(sender.id)
