import queue
import logging
import random
import time

from sms_monster import SmsMonster


log_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)
if 1:
    logging.getLogger().setLevel(logging.DEBUG)


class Pipeline(queue.Queue):
    def __init__(self):
        super().__init__(maxsize=0)

    def get_message(self, name):
        logging.debug("%s:about to get from queue", name)
        det_dict = self.get()
        logging.debug("%s:got %s from queue", name, det_dict)
        return det_dict

    def set_message(self, det_dict, name):
        logging.debug("%s:about to add %s to queue", name, det_dict)
        self.put(det_dict)
        logging.debug("%s:added %s to queue. Length %d", name, det_dict, self.qsize())


def dummy_producer(pipeline, event):
    """Pretend we're identifying objects."""
    while not event.is_set():
        message = random.randint(1, 101)
        logging.info("Producer got message: %s", message)
        pipeline.set_message(message, "Producer")

    logging.info("Producer received EXIT event. Exiting")


def consumer(pipeline, event):
    def send_sms(msg, number):
        logging.debug("send: %s", msg)
        if sms_monster is not None:
            sms_monster.simple_send(number, msg)
            logging.debug(f"actual send: {number}, {msg}")
        else:
            logging.debug(f"dummy send: {number}, {msg}")

    def relative_dict_str(dic):
        s = ''
        for k, v in dic.items():
            sign = '+' if v >= 0 else ''  # neg will already put sign
            s += f'{k}: {sign}{v}, '
        if s:
            s = s[:-2]
        return s

    def dict_str(dic):
        s = ''
        for k, v in dic.items():
            s += f'{k}: {v}, '
        if s:
            s = s[:-2]
        return s

    NUMB_TIME = 10.0
    last = {}
    last_time = time.time() - NUMB_TIME
    sms_url = None
    sms_monster = None
    while not event.is_set() or not pipeline.empty():
        this = pipeline.get_message("Consumer")
        # extract SMS details and create monster if new or changed
        sms_number = this.pop('sms_number')
        new_sms_url = this.pop('sms_url')
        if sms_url != new_sms_url:
            try:
                sms_monster = SmsMonster(new_sms_url)
                sms_url = new_sms_url
            except Exception as exc:
                pass
        delta = get_delta(last, this)
        if not delta:
            logging.debug("consumer received identical det list: %s", this)
            continue
        if time.time() > last_time + NUMB_TIME:
            last = this
            last_time = time.time()
            logging.info("Sending message: %s  (queue size=%s)", delta, pipeline.qsize())
            send_sms(f"I see: {dict_str(last)}\n  Changes: {relative_dict_str(delta)}", sms_number)

    logging.info("Consumer received EXIT event. Exiting")


def get_delta(last, this):
    symmetric_diff = set(last.items()) ^ set(this.items())
    gained_or_lost = dict(symmetric_diff).keys()
    delta = {gl: (this.get(gl, 0) - last.get(gl, 0)) for gl in gained_or_lost}
    return delta


if __name__ == '__main__':
    last = {}
    this = dict(a=1)
    assert get_delta(last, this) == dict(a=1)

    last = dict(a=1)
    this = dict(a=1, b=1)
    assert get_delta(last, this) == dict(b=1)

    last = dict(a=1)
    this = dict(a=2)
    assert get_delta(last, this) == dict(a=1)

    last = dict(a=1)
    this = dict(a=0)
    assert get_delta(last, this) == dict(a=-1)

    last = dict(a=1)
    this = dict()
    assert get_delta(last, this) == dict(a=-1)

    last = dict(a=1, b=2)
    this = dict(a=1, b=1)
    assert get_delta(last, this) == dict(b=-1)
