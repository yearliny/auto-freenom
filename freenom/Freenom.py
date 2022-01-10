# -*- coding: utf-8 -*-
import datetime
import logging
import os
import pickle
from collections import namedtuple
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

FreedomDomain = namedtuple('FreedomDomain',
                           ['id', 'domain_name', 'registration_date', 'expired_date', 'available_days', 'status',
                            'type'])


class Freenom:
    # 登陆出错消息的 css选择器
    __SELECTOR_LOGIN_ERROR = 'p.error'

    # freenom 登陆入口
    __LOGIN_URL = 'https://my.freenom.com/dologin.php'

    __RENEW_DOMAIN_URL = 'https://my.freenom.com/domains.php?submitrenewals=true'

    # 最小提前续期天数
    __MINIMUM_ADVANCE_RENEWAL = 14

    __COOKIES_NAME = 'cookies.pickle'

    def __init__(self, username, password, **kwargs):
        """
        init params
        :param username: your username
        :type username: str
        :param password: your password
        :type password: str
        """
        # path setup
        self._path = os.getcwd()
        self._cookies_path = os.path.join(self._path, Freenom.__COOKIES_NAME)
        # user setup
        self.username = username
        self.password = password
        self.domain_list = []
        self.token = ''
        # request setup
        self.headers = {
            'Host': 'my.freenom.com',
            'Origin': 'https://my.freenom.com',
            'Referer': 'https://my.freenom.com/clientarea.php',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
        }
        self.session = requests.session()
        self.session.headers = self.headers
        # 每页多少条域名 WHMCSItemsPerPage=-1， -1 为 Unlimited
        self.session.cookies.setdefault('WHMCSItemsPerPage', '-1')

        # cookies setup
        if os.path.isfile(Freenom.__COOKIES_NAME):
            with open(Freenom.__COOKIES_NAME, 'rb') as f:
                self.session.cookies.update(pickle.load(f))
        self.load_domain()

    @staticmethod
    def __is_login(soup):
        token = soup.select_one('a[href="logout.php"]')
        return token is not None

    def __get_token(self, soup):
        self.token = soup.find(name='input', attrs={'name': 'token'}).attrs['value']
        return self.token

    def __parse_domain(self, soup):
        logging.info('开始加载域名数据...')
        self.domain_list = []
        rows = soup.select('#bulkactionform > table > tbody > tr')
        now = datetime.datetime.now()

        for item in rows:
            registration_date_str = item.select_one('td.third').string
            expired_date_str = item.select_one('td.fourth').string
            registration_date = datetime.datetime.strptime(registration_date_str, '%Y-%m-%d')
            expired_date = datetime.datetime.strptime(expired_date_str, '%Y-%m-%d')

            href = urlparse(item.select_one('td.seventh a')['href'])
            query_param = parse_qs(href.query)
            freedom_domain = FreedomDomain(
                id=query_param['id'][0],
                domain_name=item.find('a').text.strip(),
                registration_date=registration_date,
                expired_date=expired_date,
                available_days=(expired_date - now).days,
                status=item.select_one('td.fifth > span').string,
                type=item.select_one('td.sixth').string
            )
            self.domain_list.append(freedom_domain)

            # sort by domain.available_days
            self.domain_list.sort(key=lambda domain: domain.available_days)
        logging.info('成功加载 %s 条域名记录！', len(self.domain_list))

    def load_domain(self):
        self.domain_list = []
        login_page = self.session.get('https://my.freenom.com/clientarea.php?action=domains')
        soup_login = BeautifulSoup(login_page.text, features='html.parser')
        # 检查是否已经登陆，如果没有登陆
        if Freenom.__is_login(soup_login):
            logging.info('检测到已经登陆')
            return self.__parse_domain(soup_login)

        # 开始登陆
        login_data = {
            'token': self.__get_token(soup_login),
            'username': self.username,
            'password': self.password,
            'rememberme': 'on'
        }
        do_login = self.session.post(Freenom.__LOGIN_URL, data=login_data)
        soup_login = BeautifulSoup(do_login.text, features='html.parser')
        if not Freenom.__is_login(soup_login):
            error_msg = soup_login.select_one(Freenom.__SELECTOR_LOGIN_ERROR).text
            return logging.error('登陆失败：%s', error_msg)
        logging.info('登陆 Freenom 成功！')
        # 保存更新 cookies 并加载数据
        with open(Freenom.__COOKIES_NAME, 'wb') as f:
            pickle.dump(self.session.cookies, f)
        self.__parse_domain(soup_login)

    def renew_one(self, domain):
        if domain.available_days > 14:
            return logging.info('【%s】 有效期为 %s 天，无需续期。', domain.domain_name, domain.available_days)

        header = {
            'Referer': 'https://my.freenom.com/domains.php?a=renewdomain&domain={}'.format(domain.id)
        }
        params = {
            'token': self.token,
            'renewalid': domain.id,
            'renewalperiod[{}]'.format(domain.id): '12M',
            'paymentmethod': 'credit'
        }
        renew_res = self.session.post(Freenom.__RENEW_DOMAIN_URL, data=params, headers=header)
        is_success = 'complete' in renew_res.url and 'Order Confirmation' in renew_res.text
        if is_success:
            logging.info('成功续期域名【%s】', domain.domain_name)
            return True
        else:
            logging.debug('续期失败 %s，页面响应 -> %s', domain.domain_name, renew_res.text)
            logging.error('续期失败 %s', domain.domain_name)
        return False

    def renew_all(self):
        ready_domain = [item for item in self.domain_list if item.available_days <= Freenom.__MINIMUM_ADVANCE_RENEWAL]
        success_count = 0
        if len(ready_domain) < 1:
            logging.info('当前没有可续期的域名，续期操作终止。')
            return success_count

        logging.info('当前有 {} 个域名需要续期，现在开始续期！'.format(len(ready_domain)))
        for domain in ready_domain:
            if self.renew_one(domain):
                success_count += 1
        logging.info('续期操作结束，成功续期 {} 个域名！'.format(len(ready_domain), success_count))
        return success_count
