"""
Backward compatibility alias for agent module.

The agent module has been moved to core/agent.py for better organization.
This file provides backward compatibility.
"""

# Import everything from the new location
from .core.agent import *  # noqa: F403, F401

# Maintain backward compatibility warnings
import warnings

warnings.warn(
    "Importing from ai_sidekick_for_splunk.agent is deprecated. "
    "Please import from ai_sidekick_for_splunk.core.agent instead.",
    DeprecationWarning,
    stacklevel=2
)