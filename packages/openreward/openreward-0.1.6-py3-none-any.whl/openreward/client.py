import os
from typing import Optional

from openreward.models import Config, SendLoopConfig
from openreward.api.rollouts.rollout import RolloutAPI
from openreward.api.environments.client import EnvironmentsAPI
from openreward.api.sandboxes import SandboxesAPI, SandboxSettings

BASE_URL = "https://api.openreward.ai"
ENVIRONMENTS_BASE_URL = "https://matrix.openreward.ai"
SANDBOXES_BASE_URL = "http://construct.openreward.ai"

OPENREWARD_API_KEY_ENV_VAR_NAME = "OPENREWARD_API_KEY"

class OpenReward:
    def __init__(self, api_key: str | None = None, base_url: str = BASE_URL, environments_base_url: str | None = None):
       
        self.api_key = api_key or os.getenv(OPENREWARD_API_KEY_ENV_VAR_NAME, None)

        if base_url == BASE_URL:
            base_url = os.getenv("OPENREWARD_URL", BASE_URL)
        self.base_url = base_url
        
        if environments_base_url:
            self.environments_base_url = environments_base_url
        else:
            self.environments_base_url = os.getenv("OPENREWARD_ENVIRONMENTS_URL", ENVIRONMENTS_BASE_URL)

        self.config = Config(
            process_name="openreward_client", 
            shutdown_timeout=10.0, 
            send_loop_config=SendLoopConfig(
                max_items=128,
                max_bytes=4_000_000, # 4MB
                max_age=1.0, # 1 second
                jitter=0.05, # 5% jitter
                ring_capacity=100000, # 10,000 items
                max_batch_items=1024,
                max_batch_bytes=8_000_000, 
                max_retries=4, 
                backoff_base=0.5, # 0.5 seconds
                backoff_factor=2.0, 
                backoff_cap=30.0, # 30 seconds
                max_upload_concurrency=1024,
                api_key=api_key,
                base_url=base_url
            )
        )
        
        self._rollout_api: Optional[RolloutAPI] = None
        self._environments_api: Optional[EnvironmentsAPI] = None

    @property
    def rollout(self) -> RolloutAPI:
        if self._rollout_api is None:
            self._rollout_api = RolloutAPI(
                send_loop_config=self.config.send_loop_config, 
                shutdown_timeout=self.config.shutdown_timeout, 
                process_name=self.config.process_name
            )
        assert self._rollout_api is not None # helping the type checker
        return self._rollout_api

    @property
    def environments(self) -> EnvironmentsAPI:
        if self._environments_api is None:
            self._environments_api = EnvironmentsAPI(
                base_url=self.environments_base_url,
                api_key=self.api_key
            )
        assert self._environments_api is not None # helping the type checker
        return self._environments_api


    def sandbox(
        self, 
        settings: SandboxSettings,
        creation_timeout: int = 60*30,
    ) -> SandboxesAPI:
        if self.api_key is None:
            raise ValueError("API key is required for sandbox API")

        return SandboxesAPI(
            base_url=SANDBOXES_BASE_URL,
            api_key=self.api_key,
            settings=settings,
            creation_timeout=creation_timeout,
        )