import queue
import logging
import random

log_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO, datefmt="%H:%M:%S.f")
if 1:
    logging.getLogger().setLevel(logging.DEBUG)


class Pipeline(queue.Queue):
    def __init__(self):
        super().__init__(maxsize=0)

    def get_message(self, name):
        logging.debug("%s:about to get from queue", name)
        value = self.get()
        logging.debug("%s:got %s from queue", name, value)
        return value

    def set_message(self, value, name):
        logging.debug("%s:about to add %s to queue", name, value)
        self.put(value)
        logging.debug("%s:added %s to queue", name, value)


def dummy_producer(pipeline, event):
    """Pretend we're identifying objects."""
    while not event.is_set():
        message = random.randint(1, 101)
        logging.info("Producer got message: %s", message)
        pipeline.set_message(message, "Producer")

    logging.info("Producer received EXIT event. Exiting")


def consumer(pipeline, event):
    def send_sms(msg):
        logging.debug("dummy send: %s", msg)

    while not event.is_set() or not pipeline.empty():
        message = pipeline.get_message("Consumer")
        logging.info(
            "Sending message: %s  (queue size=%s)",
            message,
            pipeline.qsize(),
        )
        send_sms(message)

    logging.info("Consumer received EXIT event. Exiting")
