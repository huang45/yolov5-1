import time

from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection


def log(msg):
    print(msg)


class SmsMonster:
    def __init__(self, url):
        self.connection = AuthorizedConnection(url)
        self.client = Client(self.connection)
        self.sm = self.client.sms

    def simple_send(self, number, msg):
        self.sm.send_sms([number], msg)
        log('sent: %s' % msg)

    def get_next_message_content(self):
        ll = self.sm.get_sms_list()
        """ Notes
        # No messages
        {'Count': '0', 'Messages': None}
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
        content = msg['Content'] or ''
        index = msg['Index']
        self.sm.delete_sms(index)
        return content


if __name__ == '__main__':
    NUMBER = "put your 10 digit test target phone here..."

    mon = SmsMonster(url="put the network address of your huaweii here")
    for i in range(10):
        while True:
            m = mon.get_next_message_content()
            if m is None:
                break
            print(f"received {m}")
        mon.simple_send(NUMBER, 'hi #%d @ %s ' % (i, str(time.time())))
        time.sleep(5)

