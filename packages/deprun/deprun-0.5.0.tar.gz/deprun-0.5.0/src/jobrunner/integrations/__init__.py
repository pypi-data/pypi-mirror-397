"""External integrations for job-runner.

Integrations with Git, environment variables, and other external systems.
"""

from .git import GitManager
from .env import EnvManager

__all__ = [
    'GitManager',
    'EnvManager',
]
