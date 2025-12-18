# Copyright (c) Microsoft. All rights reserved.

"""Agent Framework DevUI module - Import forwarding for compatibility."""

# This module forwards all imports from the actual implementation
# to maintain the original import pattern: from agent_framework.devui import serve

# Forward all public exports from the actual implementation
from agent_framework_devui import (
    AgentFrameworkRequest,
    CheckpointConversationManager,
    DevServer,
    DiscoveryResponse,
    EntityInfo,
    EnvVarRequirement,
    OpenAIError,
    OpenAIResponse,
    ResponseStreamEvent,
    main,
    register_cleanup,
    serve,
)

# Ensure __version__ is available
from agent_framework_devui import __version__

# Re-export everything for compatibility
__all__ = [
    "AgentFrameworkRequest",
    "CheckpointConversationManager", 
    "DevServer",
    "DiscoveryResponse",
    "EntityInfo",
    "EnvVarRequirement",
    "OpenAIError",
    "OpenAIResponse",
    "ResponseStreamEvent",
    "main",
    "register_cleanup",
    "serve",
    "__version__",
]