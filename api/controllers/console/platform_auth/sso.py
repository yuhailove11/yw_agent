"""Dify 统一认证中心 SSO 交换接口。"""

from __future__ import annotations

from flask import make_response, redirect, request
from flask_restx import Resource

from configs import dify_config
from controllers.console import console_ns
from libs.helper import extract_remote_ip
from libs.token import set_access_token_to_cookie, set_csrf_token_to_cookie, set_refresh_token_to_cookie
from services.account_service import AccountService
from services.platform_auth.sso_service import PlatformAuthSsoService


@console_ns.route("/platform-auth/sso/exchange")
class PlatformAuthSsoExchangeApi(Resource):
    def get(self):
        ticket = str(request.args.get("ticket") or "").strip()
        if not ticket:
            return {"result": "fail", "message": "ticket is required"}, 400

        exchange_result = PlatformAuthSsoService.exchange(ticket)
        token_pair = AccountService.login(exchange_result.account, ip_address=extract_remote_ip(request))
        response = make_response(redirect(dify_config.CONSOLE_WEB_URL or "/apps"))
        set_access_token_to_cookie(request, response, token_pair.access_token)
        set_refresh_token_to_cookie(request, response, token_pair.refresh_token)
        set_csrf_token_to_cookie(request, response, token_pair.csrf_token)
        return response
