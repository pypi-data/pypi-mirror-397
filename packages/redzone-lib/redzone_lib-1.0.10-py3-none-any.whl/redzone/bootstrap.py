import logging

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .settings import ENVIRONMENT, PROJECT_NAME, SENTRY_DSN
from .utils.logger import logger
from .utils.trace import Trace

if ENVIRONMENT in ["staging", "sandbox", "production"]:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            AwsLambdaIntegration(),
            LoggingIntegration(
                level=logging.DEBUG,
                event_level=logging.CRITICAL,
            ),
        ],
        environment=ENVIRONMENT,
    )

# disable 3rd party logging
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger("aiobotocore").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("httpcore").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logger.logger.setLevel(logging.DEBUG)

# initialize trace logging
Trace.initializing_logging(f"%(trace_id)s:%(levelname)s:{PROJECT_NAME}:%(message)s")
