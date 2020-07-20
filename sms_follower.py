import queue
import logging
import random
import time
import datetime
import pytz

from sms_monster import SmsMonster

TIMEZONE = pytz.timezone("Europe/London")

log_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)
if 0:
    logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger('dicttoxml').setLevel(logging.ERROR)


class Pipeline(queue.Queue):
    def __init__(self):
        super().__init__(maxsize=0)

    def get_message(self, name):
        # logging.debug("%s:about to get from queue", name)
        det_dict = self.get()
        logging.debug("%s:got %s from queue", name, det_dict)
        return det_dict

    def set_message(self, det_dict, name):
        # logging.debug("%s:about to add %s to queue", name, det_dict)
        self.put(det_dict)
        logging.debug("%s:added %s to queue. Length %d", name, det_dict, self.qsize())


def dummy_producer(pipeline, event):
    """Pretend we're identifying objects."""
    while not event.is_set():
        message = random.randint(1, 101)
        logging.info("Producer got message: %s", message)
        pipeline.set_message(message, "Producer")

    logging.info("Producer received EXIT event. Exiting")


def timestr():
    return datetime.datetime.now(tz=TIMEZONE).strftime('%H:%M:%S%z')


def fulltimestr():
    return datetime.datetime.now(tz=TIMEZONE).isoformat()


def consumer(pipeline, event):
    def send_sms(msg, number):
        logging.debug("send: %s", msg)
        if sms_monster is not None:
            sms_monster.simple_send(number, msg)
            logging.debug(f"actual send: {number}, {msg}")
        else:
            logging.info(f"dummy send: {number}, {msg}")

    def get_sms():
        logging.debug("getting sms")
        if sms_monster is not None:
            received = sms_monster.get_next_message_content() or ''
            logging.debug(f"got: {received}")
        else:
            received = ''
            logging.info(f"dummy receive: {received}")
        return received

    def relative_dict_str(dic):
        s = ''
        for k, v in sorted(dic.items()):
            sign = '+' if v >= 0 else ''  # neg will already put sign
            s += f'  {k}: {sign}{v}\n'
        if s:
            s = s[:-1]
        return s

    def dict_str(dic):
        s = ''
        for k, v in sorted(dic.items()):
            s += f'  {k}: {v}\n'
        if s:
            s = s[:-1]
        return s

    def process_input(mo, numb_secs, sms_number):
        command = get_sms().lower()
        if command == 'quiet':
            mo = 'quiet'
            send_sms("going quiet. Send 'notify' for notifications", sms_number)
        elif command == 'notify':
            mo = 'notify'
            send_sms("notifying. Send 'quiet' to prevent notifications", sms_number)
        elif command.startswith('numb'):
            try:
                numb_secs = int(command.split()[1])
                send_sms(f"changing numb time to {numb_secs} seconds", sms_number)
            except (IndexError, ValueError) as exc:
                send_sms(f"numb-time unchanged", sms_number)
        return mo, numb_secs

    while 1:
        try:
            logging.debug(">>>>> starting consumer <<<<<")
            NUMB_TIME = 10.0
            last = {}
            last_time = time.time() - NUMB_TIME
            sms_url = None
            sms_monster = None
            mode = 'notify'
            numb_secs = NUMB_TIME
            while not event.is_set() or not pipeline.empty():
                this = pipeline.get_message("Consumer")
                # extract SMS details and create monster if new or changed
                sms_number = this.pop('sms_number')
                new_sms_url = this.pop('sms_url')
                source_name = this.pop('source_name')
                if sms_url != new_sms_url:
                    try:
                        sms_monster = SmsMonster(new_sms_url)
                        sms_url = new_sms_url
                    except Exception as exc:
                        logging.exception('while instantiating new Monster')
                if 1:
                    mode, numb_secs = process_input(mode, numb_secs, sms_number)

                delta = get_delta(last, this)
                if not delta:
                    logging.debug("consumer received identical det list: %s", this)
                    continue
                if (time.time() > last_time + numb_secs) and (mode == 'notify'):
                    last = this
                    last_time = time.time()
                    logging.info("Sending message: %s  (queue size=%s)", delta, pipeline.qsize())
                    send_sms(f"At {timestr()} {source_name if source_name else 'Camera'} sees...\n"
                             f"{dict_str(last)}\n"
                             f"Changes...\n"
                             f"{relative_dict_str(delta)}\n"
                             f"Sent at {fulltimestr()}", sms_number)
                else:
                    logging.debug("numb or quiet")

            logging.info("Consumer received EXIT event. Exiting")
            return
        except Exception as exc:
            logging.exception('consumer')


def get_delta(last, this):
    """return the delta of changed classes"""
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
