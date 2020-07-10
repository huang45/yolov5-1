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

    def get_next_message_content(self):
        if self.client is None:
            self.client = self.get_client(self.connection)
            self.sm = self.client.sms
        ll = self.sm.get_sms_list()
        """ Notes
        # get_sms_list when there is 1 message...
        {'Count': '1', 'Messages': {'Message': {'Smstat': '0', 'Index': '40106', 'Phone': '+447429518822', 'Content': 'G', 
                                               'Date': '2020-07-07 19:26:02', 'Sca': None, 'SaveType': '0', 'Priority': '0', 'SmsType': '1'}
                                   }}
        # get_sms_list when there are 2 messages...
        {'Count': '2', 'Messages': {'Message': [{'Smstat': '0', 'Index': '40312', 'Phone': '+447429518822', 'Content': 'Rf', 
                                               'Date': '2020-07-09 21:51:57', 'Sca': None, 'SaveType': '0', 'Priority': '0', 'SmsType': '1'}, 
                                               {'Smstat': '0', 'Index': '40106', 'Phone': '+447429518822', 'Content': 'G', 
                                               'Date': '2020-07-07 19:26:02', 'Sca': None, 'SaveType': '0', 'Priority': '0', 'SmsType': '1'}]}}
        """
        if int(ll['Count']) == 0:
            return None
        if int(ll['Count']) > 1:
            msg = ll['Messages']['Message'][-1]
        else:
            msg = ll['Messages']['Message']
        content = msg['Content']
        index = msg['Index']
        self.sm.delete_sms(index)
        return content


if __name__ == '__main__':
    NUMBER = "xx"

    mon = SmsMonster(url="yy")
    for i in range(10):
        while True:
            m = mon.get_next_message_content()
            if m is None:
                break
            print(f"received {m}")
        mon.simple_send(NUMBER, 'hi #%d @ %s ' % (i, str(time.time())))
        time.sleep(5)

