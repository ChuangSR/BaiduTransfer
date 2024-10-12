import base64
import json
import time

import execjs
import requests
import yaml
from lxml import etree
import urllib
from urllib import parse

class BaiduTransfer:
    def __init__(self):
        with open('config.yml', 'r', encoding='utf-8') as f:
            self.conf = yaml.load(f, Loader=yaml.FullLoader)

    #获取header参数，通用的headers
    def header(self,referer=None):
        header = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://pan.baidu.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.conf["UserAgent"],
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        if referer:
            header["Referer"] = referer
        return header
    #加载js文件
    def _load_js(self):
        with open("DpLogId.js", mode="r", encoding="utf-8") as f:
            data = f.read()
        return data

    def _to_dict(self,text):
        data = {}
        text_list = text.split(",")
        for i in text_list:
            temp = i.split(":")
            temp[0] = temp[0].strip()
            temp[1] = temp[1].strip().split("\"")
            if len(temp[1]) == 3:
                temp[1] = temp[1][1]
            else:
                temp[1] = temp[1][0].split("\'")
                if len(temp[1]) == 3:
                    temp[1] = temp[1][1]
                else:
                    temp[1] = temp[1][0]
            data[temp[0]] = temp[1]
        return data
    #转存文件
    def transfer(self, surl, pwd):
        #获取两个必须的cookie BAIDUID和BAIDUID_BFESS
        response = requests.get(f'https://pan.baidu.com/s/{surl}', headers=self.header(), allow_redirects=False)
        cookies = {
            'BAIDUID': f'{response.cookies.get("BAIDUID")}',
            'BAIDUID_BFESS': f'{response.cookies.get("BAIDUID_BFESS")}',
        }

        #由BAIDUID生成的参数
        logid = base64.b64encode(cookies["BAIDUID"].encode()).decode()

        #通过js生成对应的时间戳
        context = execjs.compile(self._load_js())
        dp_logid = context.call("get_dp_logid")

        #提取码认证的参数
        data = {
            'pwd': pwd,
            'vcode': '',
            'vcode_str': '',
        }
        #认证提取码，获取BDCLND认证cookie
        response = requests.post(
            'https://pan.baidu.com/share/verify?'
            f't={int(time.time_ns() / 1000000)}'  # 时间戳
            f'&surl={surl[1:]}'  # 请求链接后面的参数
            '&channel=chunlei'  # 定值
            '&web=1'  # 定值
            '&app_id=250528'  # 定值，疑似和百度网盘的版本有关
            '&bdstoken='  # 定值
            f'&logid={logid}'  # 对于BAIDUID进行base64编码
            '&clienttype=0'  # 定值
            f'&dp-logid={dp_logid}',  # 通过js生成
            cookies=cookies,
            headers=self.header(referer=f'https://pan.baidu.com/share/init?surl={surl[1:]}&pwd={pwd}'),
            data=data,
        )
        BDCLND = response.cookies.get("BDCLND")

        #添加登录的cookie
        cookies["PANWEB"] = "1"
        cookies["BDCLND"] = BDCLND
        cookies["BDUSS"] = self.conf.get("LoginCookie").get("BDUSS")
        cookies["BDUSS_BFESS"] = self.conf.get("LoginCookie").get("BDUSS_BFESS")
        cookies["STOKEN"] = self.conf.get("LoginCookie").get("STOKEN")
        #资源页面的参数
        params = {
            'pwd': pwd,
            '_at_': f'{int(time.time_ns() / 1000000)}',
        }
        response = requests.get(f'https://pan.baidu.com/s/{surl}', params=params, cookies=cookies, headers=self.header())

        #提取登录参数和文件参数
        tree = etree.HTML(response.text)
        script = tree.xpath('//body/script')
        yun_text = script[-1].xpath("./text()")[0].split("window.yunData={")[-1].split("}")[0]
        login_text = script[-1].xpath("./text()")[0].split("locals.mset(")[-1].split(");")[0]
        yun_json = self._to_dict(yun_text)
        login_json = json.loads(login_text)

        #转存文件到对应路径
        params = {
            'shareid': yun_json.get("shareid"),  # t
            'from': yun_json.get("share_uk"),  # t
            'sekey': urllib.parse.unquote(BDCLND),  # BDCLND的值
            'ondup': 'newcopy',  # t
            'async': '1',  # t
            'channel': 'chunlei',  # t
            'web': '1',  # t
            'app_id': '250528',  # t
            'bdstoken': yun_json.get("bdstoken"),
            'logid': '',
            'clienttype': '0',
            'dp-logid': context.call("get_dp_logid"),
        }
        data = {
            'fsidlist': f'[{login_json.get("file_list")[0].get("fs_id")}]',
            'path': f'{self.conf.get("SavePath")}',
        }
        response = requests.post('https://pan.baidu.com/share/transfer', params=params, cookies=cookies,
                                 headers=self.header(referer=f'https://pan.baidu.com/s/{surl}?pwd={pwd}'), data=data)
        print(response.text)
surl = "1cUdoqTfWdMNjaKa9vkM6kA"
pwd = "1234"
transfer = BaiduTransfer()
transfer.transfer(surl,pwd)
