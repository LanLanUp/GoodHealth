#! /usr/bin/python

import requests
import json
import re
import datetime
import time
import pytz as pytz
import sys
import os
import getopt
import random


class GoodHealth(object):
    def __init__(self, user, pwd):
        requests.packages.urllib3.disable_warnings()
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/7.0.4 Mobile/16B91 Safari/605.1.15'
        }
        self.user = str(user)
        self.pwd = str(pwd)
        self.session = requests.Session()
        self.__hack_ip()
        self.__stu_login()

    def __NEU_login(self, url):
        info = self.session.get(url)
        info.raise_for_status()
        lt = re.findall("name=\"lt\" value=\"(.*?)\" />", info.text)[0]
        execution = re.findall("name=\"execution\" value=\"(.*?)\" />", info.text)[0]
        post_data = {
            'rsa': self.user + self.pwd + lt,
            'ul': len(self.user),
            'pl': len(self.pwd),
            'lt': lt,
            'execution': execution,
            '_eventId': 'submit',
        }
        ret = self.session.post(url, headers=self.__headers, data=post_data)
        ret.raise_for_status
        return ret

    def __hack_ip(self):
        login_post = self.__NEU_login(
            r'https://pass.neu.edu.cn/tpass/login?service=https%3A%2F%2Fwebvpn.neu.edu.cn%2Flogin%3Fcas_login%3Dtrue'
        )
        if login_post.url == 'https://webvpn.neu.edu.cn/':
            print('[ GoodHealth ] Successful login the webvpn.')
        else:
            raise RuntimeError('[ GoodHealth ] failed to login the webvpn.')

    def __stu_login(self):
        login_post = self.__NEU_login(
            r'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421e0f6528f693e6d45300d8db9d6562d/tpass/login'
        )
        if 'tp_up' in login_post.url:
            print('[ GoodHealth ] Successful login the portal.')
        else:
            raise RuntimeError('[ GoodHealth ] failed to login the portal.')

    def get_status(self, date=None):
        """Check whether your info have reported.

        Args:
            date (string): The date you want to check. Defaults to today.
                            ex. '2022-01-18'

        Returns:
            bool: Whether your info have reported.
        """
        if not date:
            date = datetime.datetime.fromtimestamp(
                int(time.time()), pytz.timezone('Asia/Shanghai')
            ).strftime('%Y-%m-%d')
        status_page = self.session.get(
            'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421f5ba5399373f7a4430068cb9d6502720645809/api/notes',
            verify=False,
        )
        status_page.raise_for_status()
        status = json.loads(status_page.text)['data']
        status.reverse()
        for i in status:
            if i['created_on'] == date:
                return True
        return False

    def sign(self, location_ch=None):
        """Post your state of health.

        Args:
            location_ch (dict): The location you changed. Defaults to None i.e. the location is not changed.
                                ex. {
                                    'country': "中国",
                                    'province': "辽宁省",
                                    'city': "沈阳市"
                                }

        Raises:
            RuntimeError: post or validate failed.
        """
        start_page = self.session.get(
            'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421f5ba5399373f7a4430068cb9d6502720645809/mobile/notes/create',
            verify=False,
        )
        start_page.raise_for_status()
        get_profiles = self.session.get(
            'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421f5ba5399373f7a4430068cb9d6502720645809/api/profiles/'
            + self.user
        )
        get_profiles.raise_for_status()
        prof_dict = json.loads(get_profiles.text)
        if location_ch:
            data = {
                '_token': re.findall(
                    "\"csrf-token\" content=\"(.*?)\">", start_page.text
                )[0],
                'jibenxinxi_shifoubenrenshangbao': '1',
                'profile[xuegonghao]': self.user,
                'profile[xingming]': prof_dict['data']['xingming'],
                'profile[suoshubanji]': prof_dict['data']['suoshubanji'],
                'jiankangxinxi_muqianshentizhuangkuang': '正常',
                'xingchengxinxi_weizhishifouyoubianhua': '1',
                'xingchengxinxi_guojia': location_ch['country'],
                'xingchengxinxi_shengfen': location_ch['province'],
                'xingchengxinxi_chengshi': location_ch['city'],
                'cross_city': '无',
                'qitashixiang_qitaxuyaoshuomingdeshixiang': '',
                'credits': '1',
                'travels': [],
            }
        else:
            data = {
                '_token': re.findall(
                    "\"csrf-token\" content=\"(.*?)\">", start_page.text
                )[0],
                'jibenxinxi_shifoubenrenshangbao': '1',
                'profile[xuegonghao]': self.user,
                'profile[xingming]': prof_dict['data']['xingming'],
                'profile[suoshubanji]': prof_dict['data']['suoshubanji'],
                'jiankangxinxi_muqianshentizhuangkuang': '正常',
                'xingchengxinxi_weizhishifouyoubianhua': '0',
                'cross_city': '无',
                'qitashixiang_qitaxuyaoshuomingdeshixiang': '',
                'credits': '1',
                'travels': [],
            }

        post_notes = self.session.post(
            'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421f5ba5399373f7a4430068cb9d6502720645809/api/notes',
            data=data,
            verify=False,
        )
        post_notes.raise_for_status()
        if post_notes.text == '':
            print('[ GoodHealth ] Post successful.')
        else:
            print(post_notes.text)
            raise RuntimeError('[ GoodHealth ] Post failure.')

        if self.get_status:
            print('[ GoodHealth ] All done!')
        else:
            raise RuntimeError('[ GoodHealth ] No record was detected!')


# the student id and password.
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]

CHANGE_CITY = None
# seconds delayed.
DELAY = 0

try:
    opts, args = getopt.getopt(
        sys.argv[1:], "hu:p:c:d", ["username=", "password=", "ccity=", "delay"]
    )
except getopt.GetoptError:
    print('GoodHealth.py -u <username> -p <password>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('GoodHealth.py -u <username> -p <password>')
        sys.exit()
    elif opt in ("-u", "--username"):
        USERNAME = arg
    elif opt in ("-p", "--password"):
        PASSWORD = arg
    elif opt in ("-c", "--ccity"):
        loc = re.split('[,，]', arg)
        CHANGE_CITY = {'country': loc[0], 'province': loc[1], 'city': loc[2]}
    elif opt in ("-d", "--delay"):
        DELAY = random.randint(0, 1800)

time.sleep(DELAY)
goodhealth = GoodHealth(USERNAME, PASSWORD)
goodhealth.sign(CHANGE_CITY)
