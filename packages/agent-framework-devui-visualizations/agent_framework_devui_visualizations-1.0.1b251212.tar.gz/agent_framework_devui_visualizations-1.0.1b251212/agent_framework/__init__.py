# Copyright (c) Microsoft. All rights reserved.

"""Agent Framework namespace package."""

# This is a namespace package - it allows multiple packages to contribute
# to the same namespace. This enables the original import pattern:
# from agent_framework.devui import serve

__path__ = __import__('pkgutil').extend_path(__path__, __name__)