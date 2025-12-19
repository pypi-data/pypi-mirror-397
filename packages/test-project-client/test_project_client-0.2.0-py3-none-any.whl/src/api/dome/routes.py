from fastapi import APIRouter, Depends
from src.api.dependencies import get_context
from src.business.context import ServiceContext
from src.business.dome.types import (
)
from src.business.dome.actions import (
)
import src.platform.hooks as platform_hooks

router = APIRouter(prefix="/dome", tags=["dome"])

