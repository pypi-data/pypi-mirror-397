import asyncio
import json
from typing import Any, Dict, Optional

import boto3
import httpx

from .errors import AppError


async def _get_aws_secrets(secret_name: str, region: str = "ca-central-1") -> Dict[str, Any]:
    def _fetch():
        client = boto3.client("secretsmanager", region_name=region)
        resp = client.get_secret_value(SecretId=secret_name, VersionStage="AWSCURRENT")
        secret_str = resp.get("SecretString") or ""
        return json.loads(secret_str)

    try:
        return await asyncio.to_thread(_fetch)
    except Exception as e:
        raise AppError(e)


class AuthService:
    @staticmethod
    async def _get_api_token(secret_name: str) -> str:
        secrets = await _get_aws_secrets(secret_name)
        try:
            return secrets["API_TOKEN"]
        except Exception as e:
            raise AppError(f"API_TOKEN not found in secret {secret_name}: {e}", 400)

    @staticmethod
    async def get_hubspot_access_token(
        app: str = "crm",
        secret_name: str = "hs-oauth-manager",
        api_url: str = "https://6jp43hzm45.execute-api.ca-central-1.amazonaws.com/prod/get-secret",
        timeout_seconds: float = 20.0,
    ) -> str:
        try:
            api_token = await AuthService._get_api_token(secret_name)

            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                res = await client.get(
                    api_url,
                    params={"app": app},
                    headers={"Authorization": f"Bearer {api_token}"},
                )

            if res.status_code < 200 or res.status_code >= 300:
                raise AppError(f"Failed to fetch token: {res.status_code} {res.text}", res.status_code)

            data = res.json()
            if "token" not in data:
                raise AppError("Response JSON missing 'token'", 500)

            return data["token"]

        except AppError:
            raise
        except Exception:
            raise AppError("Failed to authenticate with HubSpot", 401)
