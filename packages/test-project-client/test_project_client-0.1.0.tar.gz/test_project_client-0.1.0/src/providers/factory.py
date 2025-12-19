from functools import lru_cache
import logging
from src.config import Settings
from src.business.context import ServiceContext
from src.providers.openai.raw import OpenaiClientfrom src.providers.middesk.raw import MiddeskClient
class ProviderFactory:
    def __init__(self, settings: Settings):
        self.settings = settings

    def create_context(self) -> ServiceContext:
        return ServiceContext(
            config=self.settings,
            logger=logging.getLogger("platform"),
                        openai=self._create_openai_client(),
                        middesk=self._create_middesk_client(),
                    )

        def _create_openai_client(self) -> OpenaiClient:
        return OpenaiClient(
            base_url=self.settings.OPENAI_BASE_URL,
            token=self.settings.OPENAI_API_KEY
        )
        def _create_middesk_client(self) -> MiddeskClient:
        return MiddeskClient(
            base_url=self.settings.MIDDESK_BASE_URL,
            token=self.settings.MIDDESK_API_KEY
        )
    