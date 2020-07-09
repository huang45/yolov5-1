import time

from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection


def log(msg):
    print(msg)


class SmsMonster:
    def __init__(self, url):
        self.connection = self.get_connection(url)
        self.client = None
        self.sm = None

    def get_connection(self, url):
        log('getting connection')
        con = AuthorizedConnection(url)
        log('got connected')
        return con

    def get_client(self, con):
        log('getting client')
        cli = Client(con)
        log('got client')
        return cli

    def simple_send(self, number, msg):
        if self.client is None:
            self.client = self.get_client(self.connection)
            self.sm = self.client.sms
        self.sm.send_sms([number], msg)
        log('sent: %s' % msg)


if __name__ == '__main__':
    NUMBER = "xx"

    mon = SmsMonster(url="yy")
    for i in range(10):
        mon.simple_send(NUMBER, 'hi #%d @ %s ' % (i, str(time.time())))
        time.sleep(5)

