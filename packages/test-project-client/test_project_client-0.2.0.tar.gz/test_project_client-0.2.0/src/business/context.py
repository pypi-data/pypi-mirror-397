from dataclasses import dataclass
import logging
from src.config import Settings
from src.providers.openai.raw import OpenaiClientfrom src.providers.middesk.raw import MiddeskClientfrom src.providers.dome.raw import DomeClient
@dataclass
class ServiceContext:
    config: Settings
    logger: logging.Logger
        openai: OpenaiClient        middesk: MiddeskClient        dome: DomeClient    