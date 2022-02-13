#! /usr/bin/python

import requests
import json
import re
import datetime
import time
import pytz
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
        self.__user = str(user)
        self.__pwd = str(pwd)
        self.__session = requests.Session()
        self.__vpn = False

    def __NEU_login(self, url):
        info = self.__session.get(url)
        info.raise_for_status()
        lt = re.findall("name=\"lt\" value=\"(.*?)\" />", info.text)[0]
        execution = re.findall("name=\"execution\" value=\"(.*?)\" />", info.text)[0]
        post_data = {
            'rsa': self.__user + self.__pwd + lt,
            'ul': len(self.__user),
            'pl': len(self.__pwd),
            'lt': lt,
            'execution': execution,
            '_eventId': 'submit',
        }
        ret = self.__session.post(url, headers=self.__headers, data=post_data)
        ret.raise_for_status
        return ret

    def hack_ip(self):
        login_post = self.__NEU_login(
            r'https://pass.neu.edu.cn/tpass/login?service=https%3A%2F%2Fwebvpn.neu.edu.cn%2Flogin%3Fcas_login%3Dtrue'
        )
        if login_post.url == 'https://webvpn.neu.edu.cn/':
            self.__vpn = True
            print('[ GoodHealth ] Successful login the webvpn.')
        else:
            raise RuntimeError('[ GoodHealth ] failed to login the webvpn.')

    def normal_ip(self):
        self.__vpn = False

    def stu_login(self):
        login_post = self.__NEU_login(
            r'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421e0f6528f693e6d45300d8db9d6562d/tpass/login'
            if self.__vpn
            else r'https://pass.neu.edu.cn/tpass/login'
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
        status_page = self.__session.get(
            r'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421f5ba5399373f7a4430068cb9d6502720645809/api/notes'
            if self.__vpn
            else r'https://e-report.neu.edu.cn/api/notes',
            verify=False,
        )
        status_page.raise_for_status()
        status = json.loads(status_page.text)['data']
        status.reverse()
        for i in status:
            if i['created_on'] == date:
                return True
        return False

    def sign(self, location_ch=None, force=False):
        """Post your state of health.

        Args:
            location_ch (dict): The location you changed. Defaults to None i.e. the location is not changed.
                                ex. {
                                    'country': "中国",
                                    'province': "辽宁省",
                                    'city': "沈阳市"
                                }
            force (bool): Force running even if it has been reported today.

        Raises:
            RuntimeError: post or validate failed.
        """
        if self.get_status() and not force:
            print('[ GoodHealth ] You have reported today!')
            return

        start_page = self.__session.get(
            r'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421f5ba5399373f7a4430068cb9d6502720645809/mobile/notes/create'
            if self.__vpn
            else r'https://e-report.neu.edu.cn/mobile/notes/create',
            verify=False,
        )
        start_page.raise_for_status()
        get_profiles = self.__session.get(
            (
                r'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421f5ba5399373f7a4430068cb9d6502720645809/api/profiles/'
                if self.__vpn
                else r'https://e-report.neu.edu.cn/api/profiles/'
            )
            + self.__user
        )
        get_profiles.raise_for_status()
        prof_dict = json.loads(get_profiles.text)
        if location_ch:
            data = {
                '_token': re.findall(
                    "\"csrf-token\" content=\"(.*?)\">", start_page.text
                )[0],
                'jibenxinxi_shifoubenrenshangbao': '1',
                'profile[xuegonghao]': self.__user,
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
                'profile[xuegonghao]': self.__user,
                'profile[xingming]': prof_dict['data']['xingming'],
                'profile[suoshubanji]': prof_dict['data']['suoshubanji'],
                'jiankangxinxi_muqianshentizhuangkuang': '正常',
                'xingchengxinxi_weizhishifouyoubianhua': '0',
                'cross_city': '无',
                'qitashixiang_qitaxuyaoshuomingdeshixiang': '',
                'credits': '1',
                'travels': [],
            }

        post_notes = self.__session.post(
            r'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421f5ba5399373f7a4430068cb9d6502720645809/api/notes'
            if self.__vpn
            else r'https://e-report.neu.edu.cn/api/notes',
            data=data,
            verify=False,
        )
        post_notes.raise_for_status()
        if post_notes.text == '':
            print('[ GoodHealth ] Post successful.')
        else:
            print(post_notes.text)
            raise RuntimeError('[ GoodHealth ] Post failure.')

        if self.get_status():
            print('[ GoodHealth ] All done!')
            return
        else:
            raise RuntimeError('[ GoodHealth ] No record was detected!')

    def run(self, location_ch=None, force=False, vpn='off'):
        try:
            if vpn.lower() == 'on':
                self.hack_ip()
                self.stu_login()
                self.sign(location_ch=location_ch, force=force)
            elif vpn.lower() == 'first':
                try:
                    self.hack_ip()
                    self.stu_login()
                    self.sign(location_ch=location_ch, force=force)
                except:
                    self.normal_ip()
                    self.stu_login()
                    self.sign(location_ch=location_ch, force=force)
            else:
                self.normal_ip()
                self.stu_login()
                self.sign(location_ch=location_ch, force=force)
            return True
        except Exception as e:
            print(e)
            return False


# the student id and password.
try:
    USERNAME = os.environ["GHUSERNAME"]
    PASSWORD = os.environ["GHPASSWORD"]
except KeyError:
    USERNAME = None
    PASSWORD = None

try:
    CHANGE_CITY = os.environ["GHCITY"]
except KeyError:
    CHANGE_CITY = None

# seconds delayed.
try:
    DELAY = os.environ["GHDELAY"]
except KeyError:
    DELAY = 0

try:
    FORCE = os.environ["GHFORCE"]
except KeyError:
    FORCE = False

# Using webvpn login.
try:
    VPN = os.environ["GHVPN"]
except KeyError:
    VPN = 'off'

# Using ServerChan report error.
# https://sct.ftqq.com/
try:
    SENDKEY = os.environ["GHSENDKEY"]
except KeyError:
    SENDKEY = None

try:
    opts, args = getopt.getopt(
        sys.argv[1:],
        "hu:p:c:dv:s:f",
        ["username=", "password=", "ccity=", "delay", "vpn=", "sendkey=", 'force'],
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
    elif opt in ("-v", "--vpn"):
        VPN = arg
    elif opt in ("-s", "--sendkey"):
        SENDKEY = arg
    elif opt in ("-f", "--force"):
        FORCE = True

time.sleep(DELAY)
users = re.split('[,，]', USERNAME)
passwds = re.split('[,，]', PASSWORD)
ret = []
for user, passwd in zip(users, passwds):
    print('[ GoodHealth ] Signing for {}.'.format(user))
    goodhealth = GoodHealth(user, passwd)
    r = goodhealth.run(location_ch=CHANGE_CITY, force=FORCE, vpn=VPN)
    ret.append(r)

if False in ret:
    fuser = [x for x, y in zip(users, ret) if not y]
    if SENDKEY:
        msg = "The following accounts failed to run:\n"
        for i in fuser:
            msg = msg + "* {}\n".format(i)
        r = requests.get(
            'https://sctapi.ftqq.com/' + SENDKEY + '.send',
            params=dict(title='GoodHealth goes wrong!', desp=msg),
        )
    print('[ GoodHealth ] The following accounts failed to run:')
    for i in fuser:
        print('* {}'.format(i))
    raise RuntimeError('[ GoodHealth ] Something goes wrong!')
