import os
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def init_sentry():
    if os.getenv('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=os.environ['SENTRY_DSN'],
            integrations=[
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR,
                ),
            ],
            traces_sample_rate=1.0
        )