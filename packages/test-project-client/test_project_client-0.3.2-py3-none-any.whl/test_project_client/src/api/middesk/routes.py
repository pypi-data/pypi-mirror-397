from fastapi import APIRouter, Depends
from src.api.dependencies import get_context
from src.business.context import ServiceContext
from src.business.middesk.types import (
)
from src.business.middesk.actions import (
)
import src.platform.hooks as platform_hooks

router = APIRouter(prefix="/middesk", tags=["middesk"])

