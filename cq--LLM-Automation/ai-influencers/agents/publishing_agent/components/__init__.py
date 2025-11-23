"""
Publishing Agent Components

This package contains the core components for the publishing agent.
"""

# Make components available for import
try:
    from .config import (
        TWITTER_CONFIG,
        DRY_RUN,
        load_persona,
        SCHEDULES_DIR,
        LOG_CSV,
        PLATFORM_LIMITS
    )
except ImportError:
    TWITTER_CONFIG = {}
    DRY_RUN = True
    load_persona = lambda x: {"Persona_ID": x}
    SCHEDULES_DIR = None
    LOG_CSV = None
    PLATFORM_LIMITS = {}

try:
    from .nodes import prepare_post, publish_post
except ImportError:
    prepare_post = None
    publish_post = None

try:
    from .state import PublishState
except ImportError:
    PublishState = None

__all__ = [
    'TWITTER_CONFIG',
    'DRY_RUN',
    'load_persona',
    'SCHEDULES_DIR',
    'LOG_CSV',
    'PLATFORM_LIMITS',
    'prepare_post',
    'publish_post',
    'PublishState'
]
