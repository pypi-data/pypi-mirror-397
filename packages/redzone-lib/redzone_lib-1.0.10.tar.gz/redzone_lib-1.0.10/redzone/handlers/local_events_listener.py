"""
This file is exclusively for local development
It emulates the SQS Lambda Trigger by polling a queue
and sending the transformed messages to the events_listener
"""

import asyncio
import json
import logging
import os
import traceback
from signal import SIGTERM, signal
from typing import Callable

from microgue.queues.abstract_queue import AbstractQueue

from .. import bootstrap  # noqa
from ..utils.logger import logger
from ..utils.trace import Trace


class Queue(AbstractQueue):
    queue_url = os.environ.get("QUEUE_URL")


class LocalListener:
    terminating = False

    def __init__(self):
        signal(SIGTERM, self.terminate)

    def terminate(self, *args, **kwargs):
        self.terminating = True

    async def listen(self, events_listener: Callable):
        queue = Queue()
        while not self.terminating:
            # disable logging in local until a message is received
            logging.getLogger().setLevel(logging.CRITICAL)
            # poll the event queue for events
            for message in queue.receive(1):
                # enable logging after a message is received
                logging.getLogger().setLevel(logging.DEBUG)
                try:
                    # convert queue message to lambda event
                    data = {
                        "Records": [
                            {
                                "body": json.dumps(message.data),
                            },
                        ],
                    }
                    context = None

                    # for local testing skip messages produced by other engineers
                    trace_id = message.data.get("detail", {}).get("trace_id", None)
                    if trace_id != os.getenv("LOGNAME", "test")[:Trace.length]:  # fmt: skip
                        queue._queue_client.change_message_visibility(
                            QueueUrl=queue.queue_url,
                            ReceiptHandle=message.id,
                            VisibilityTimeout=0,
                        )
                        await asyncio.sleep(1)
                        continue

                    # send the data to the event listener
                    await events_listener(data, context)

                    # delete the events from the queue
                    queue.delete(message)
                except Exception as e:
                    # log the error and let the message return to the queue
                    logger.debug(str(e))
                    logger.debug(traceback.format_exc())

            # reset trace_id for each iteration
            Trace.static_trace_id = None
