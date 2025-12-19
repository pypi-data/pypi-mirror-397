import importlib
import os
import sys

sys.path.insert(0, os.getcwd())
settings = importlib.import_module("settings")
sys.path.pop(0)

##############################
# SETTINGS
##############################
# api_creator.py
ENVIRONMENT = getattr(settings, "ENVIRONMENT", "")
PROJECT_NAME = getattr(settings, "PROJECT_NAME", "")
REGION = getattr(settings, "REGION", "")
VERSION = getattr(settings, "VERSION", "")

# auth_service.py
AUTH_SERVICE_URL = getattr(settings, "AUTH_SERVICE_URL", "")

# bootstrap.py
SENTRY_DSN = getattr(settings, "SENTRY_DSN", "")

# cache.py
CACHE_HOST = getattr(settings, "CACHE_HOST", "")
CACHE_PREFIX = getattr(settings, "CACHE_PREFIX", "")

# database.py
DATABASE_HOST = getattr(settings, "DATABASE_HOST", "")
REPLICA_DATABASE_HOST = getattr(settings, "REPLICA_DATABASE_HOST", "")
MIGRATION_DATABASE_HOST = getattr(settings, "MIGRATION_DATABASE_HOST", "")
DATABASE_NAME = getattr(settings, "DATABASE_NAME", "")
DATABASE_PORT = getattr(settings, "DATABASE_PORT", "")
DATABASE_USERNAME = getattr(settings, "DATABASE_USERNAME", "")
DATABASE_PASSWORD = getattr(settings, "DATABASE_PASSWORD", "")

# event_bus.py
EVENT_BUS_NAME = getattr(settings, "EVENT_BUS_NAME", "")

# service_token.py
CLIENT_ID = getattr(settings, "CLIENT_ID", "")
CLIENT_SECRET = getattr(settings, "CLIENT_SECRET", "")

# workflow.py
WORKFLOW_TABLE_NAME = getattr(settings, "WORKFLOW_TABLE_NAME", "")
