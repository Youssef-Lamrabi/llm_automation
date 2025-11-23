# agents/publishing_agent/__init__.py

# Legacy scheduling functions (optional, require apscheduler)
try:
    from .graph import run_twitter, run_linkedin, run_medium, run_reddit, run_instagram
except ImportError as e:
    # apscheduler not installed or other import issues
    run_twitter = None
    run_linkedin = None
    run_medium = None
    run_reddit = None
    run_instagram = None

# Integration with orchestrator (core functionality)
try:
    from .agent import publish_content, agent, state
except ImportError:
    # If agent.py doesn't exist or has import issues, provide None
    publish_content = None
    agent = None
    state = None

__all__ = [
    'run_twitter', 'run_linkedin', 'run_medium', 'run_reddit', 'run_instagram',
    'publish_content', 'agent', 'state'
]
