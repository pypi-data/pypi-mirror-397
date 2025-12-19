from fastapi import APIRouter, Depends
from src.api.dependencies import get_context
from src.business.context import ServiceContext
from src.business.openai.types import (
)
from src.business.openai.actions import (
)
import src.platform.hooks as platform_hooks

router = APIRouter(prefix="/openai", tags=["openai"])

