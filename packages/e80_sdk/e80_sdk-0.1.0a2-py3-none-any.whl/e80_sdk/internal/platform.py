import asyncio
from e80_sdk.internal.environment import Environment, UserApiKey, JobToken
from e80_sdk.internal.httpx_async import async_client
from pydantic import BaseModel


class PlatformClient:
    _env: Environment

    def __init__(self, env: Environment):
        self._env = env

    async def create_sandbox(self) -> "CreateSandboxResponse":
        headers = {}
        if isinstance(self._env.identity, UserApiKey):
            headers["authorization"] = f"Bearer {self._env.identity.api_key}"
        elif isinstance(self._env.identity, JobToken):
            headers["x-8080-job-token"] = self._env.identity.job_token

        resp = await async_client.post(
            f"{self._env.base_platform_url}/api/sandbox/{self._env.organization_slug}/{self._env.project_slug}/deploy",
            headers=headers,
        )
        resp.raise_for_status()
        # TODO: Remove this sleep.
        # The endpoint returns the service when it is registered, but we must wait
        # for the service to be ready in the endpoint.
        await asyncio.sleep(10)
        return CreateSandboxResponse.model_validate(resp.json())


class CreateSandboxResponse(BaseModel):
    address: str
    auth_token: str
