# -*- coding:utf-8 -*-
# Author: Suummmmer
# Date: 2019-08-13

import base64
import json
import pickle
import requests
# import ast
import copy
import urllib.parse as parse
from config import conf_template as tpl


class Sub2Conf(object):
    def __init__(self, subs_url=None, conf_url=None):
        # 订阅原始数据
        self.origin = []

        self.subs_url = subs_url
        self.conf_url = conf_url

        # 解析后配置
        try:
            with open("/etc/v2rayL/ndata", "rb") as f:
                self.saved_conf = pickle.load(f)
        except:
            self.saved_conf = {
                "local": {},
                "subs": {}
            }

        self.conf = dict(self.saved_conf['local'], **self.saved_conf['subs'])

        '''
        self.conf结构
        {
            "地区"： "配置"
        }

        配置为解析得到的内容 + 协议
        '''

    def b642conf(self, prot, tp, b64str):
        """
        base64转化为dict类型配置
        :param prot:
        :param tp:
        :param b64str:
        :return:
        """
        if prot == "vmess":
            ret = json.loads(parse.unquote(base64.b64decode(b64str+"==").decode()).replace("\'", "\""))
            region = ret['ps']

        elif prot == "shadowsocks":
            string = b64str.split("#")
            cf = string[0].split("@")
            if len(cf) == 1:
                tmp = parse.unquote(base64.b64decode(cf[0]+"==").decode())
            else:
                tmp = parse.unquote(base64.b64decode(cf[0]+"==").decode() + "@" + cf[1])
                print(tmp)
            ret = {
                "method": tmp.split(":")[0],
                "port": tmp.split(":")[2],
                "password": tmp.split(":")[1].split("@")[0],
                "add": tmp.split(":")[1].split("@")[1],
            }
            region = parse.unquote(string[1])

        ret["prot"] = prot
        if tp == 0:
            if region in self.saved_conf["subs"]:
                region = region + "_local"
        self.saved_conf[["local", "subs"][tp]][region] = ret

    def setconf(self, region, http, socks, proxy):
        """
        生成配置
        :param region: 当前VPN别名
        :param http: http端口
        :param socks: socks端口
        :return:
        """
        use_conf = self.conf[region]
        conf = copy.deepcopy(tpl)
        conf["inbounds"][0]["port"] = socks
        conf["inbounds"][1]["port"] = http

        #  如果是vmess
        if use_conf['prot'] == "vmess":
            conf['outbounds'][0]["protocol"] = "vmess"
            conf['outbounds'][0]["settings"]["vnext"] = list()
            conf['outbounds'][0]["settings"]["vnext"].append({
                "address": use_conf["add"],
                "port": int(use_conf["port"]),
                "users": [
                    {
                        "id": use_conf["id"],
                        "alterId": int(use_conf["aid"]),
                        "security": "auto",
                        "level": 8,
                    }
                ]
            })
            # webSocket 协议
            if use_conf["net"] == "ws":
                conf['outbounds'][0]["streamSettings"] = {
                    "network": use_conf["net"],
                    "security": "tls" if use_conf["tls"] else "",
                    "tlssettings": {
                        "allowInsecure": True,
                        "serverName": use_conf["host"] if use_conf["tls"] else ""
                    },
                    "wssettings": {
                        "connectionReuse": True,
                        "headers": {
                            "Host": use_conf['host']
                        },
                        "path": use_conf["path"]
                    }
                }
            # mKcp协议
            elif use_conf["net"] == "kcp":
                conf['outbounds'][0]["streamSettings"] = {
                    "network": use_conf["net"],
                    "kcpsettings": {
                        "congestion": False,
                        "downlinkCapacity": 100,
                        "header": {
                            "type": use_conf["type"] if use_conf["type"] else "none"
                        },
                        "mtu": 1350,
                        "readBufferSize": 1,
                        "tti": 50,
                        "uplinkCapacity": 12,
                        "writeBufferSize": 1
                    },
                    "security": "tls" if use_conf["tls"] else "",
                    "tlssettings": {
                        "allowInsecure": True,
                        "serverName": use_conf["host"] if use_conf["tls"] else ""
                    }
                }
            # tcp
            elif use_conf["net"] == "tcp":
                conf['outbounds'][0]["streamSettings"] = {
                    "network": use_conf["net"],
                    "security": "tls" if use_conf["tls"] else "",
                    "tlssettings": {
                        "allowInsecure": True,
                        "serverName": use_conf["host"] if use_conf["tls"] else ""
                    },
                    "tcpsettings": {
                        "connectionReuse": True,
                        "header": {
                            "request": {
                                "version": "1.1",
                                "method": "GET",
                                "path": [use_conf["path"]],
                                "headers": {
                                    "User-Agent": ["Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"],
                                    "Accept-Encoding": ["gzip, deflate"],
                                    "Connection": ["keep-alive"],
                                    "Pragma": "no-cache",
                                    "Host": [use_conf["host"]]
                                }
                            },
                            "type": use_conf["type"]
                        }
                    } if use_conf["type"] != "none" else {}
                }
            # QUIC
            # elif use_conf["net"] == "quic":
            #     conf['outbounds'][0]["streamSettings"] = {
            #         "network": use_conf["net"],
            #         "security": "tls" if use_conf["tls"] else "none",
            #         "tlssettings": {
            #             "allowInsecure": True,
            #             "serverName": use_conf["host"]
            #         },
            #         "quicsettings": {
            #             "headers": {
            #                 "type": use_conf['type']
            #             },
            #             "key":
            #         }
            #     }
        # 如果是ss
        elif use_conf['prot'] == "shadowsocks":
            conf['outbounds'][0]["protocol"] = "shadowsocks"
            conf['outbounds'][0]["settings"]["servers"] = list()
            conf['outbounds'][0]["settings"]["servers"].append({
                "address": use_conf["add"],
                "port": int(use_conf["port"]),
                "password": use_conf["password"],
                "ota": False,
                "method": use_conf["method"]
            })
            conf['outbounds'][0]["streamSettings"] = {
                "network": "tcp"
            }
        else:
            raise MyException("不支持的协议类型")

        # 是否进行透明代理
        if proxy and use_conf['prot'] == "vmess":
            # 修改入站协议

            conf["inbounds"].append({
                "tag": "transparent",
                "port": 12345,
                "protocol": "dokodemo-door",
                "settings": {
                    "network": "tcp,udp",
                    "followRedirect": True,
                    "timeout": 30
                },
                "sniffing": {
                    "enabled": True,
                    "destOverride": [
                        "http",
                        "tls"
                    ]
                },
                "streamSettings": {
                    "sockopt": {
                        "tproxy": "tproxy"  # 透明代理使用 TPROXY 方式
                    }
                }
            })

            # 配置dns
            conf['dns']["servers"] = [
                "8.8.8.8",  # 非中国大陆域名使用 Google 的 DNS
                "1.1.1.1",
                "114.114.114.114",
                {
                    "address": "223.5.5.5",
                    "port": 53,
                    "domains": [
                        "geosite:cn",
                        "ntp.org",
                        use_conf['host']
                    ]
                }
            ]

            # 每一个outbounds添加mark
            conf['outbounds'][0]["streamSettings"]["sockopt"] = {"mark": 255}
            conf['outbounds'][1]["settings"] = {"domainStrategy": "UseIP"}
            conf['outbounds'][1]["streamSettings"] = dict()
            conf['outbounds'][1]["streamSettings"]["sockopt"] = {"mark": 255}

            conf['outbounds'].append({
                "tag": "dns-out",
                "protocol": "dns",
                "streamSettings": {
                    "sockopt": {
                        "mark": 255
                    }
                }
            })
            # 配置路由
            conf['routing']["rules"].append({
                "type": "field",
                "inboundTag": [
                    "transparent"
                ],
                "port": 53,   # 劫持53端口UDP流量，使用V2Ray的DNS
                "network": "udp",
                "outboundTag": "dns-out"
            })
            conf['routing']['rules'].append({
                "type": "field",
                "inboundTag": [
                    "transparent"
                ],
                "port": 123,  # 直连123端口UDP流量（NTP 协议）
                "network": "udp",
                "outboundTag": "direct"
            })
            conf["routing"]["rules"].append({
                "type": "field",  # 设置DNS配置中的国内DNS服务器地址直连，以达到DNS分流目的
                "ip": [
                    "223.5.5.5",
                    "114.114.114.114"
                ],
                "outboundTag": "direct"
            })
            conf["routing"]["rules"].append({
                "type": "field",
                "ip": [
                    "8.8.8.8",  # 设置 DNS 配置中的国内 DNS 服务器地址走代理，以达到DNS分流目的
                    "1.1.1.1"
                ],
                "outboundTag": "proxy"
            })
            conf["routing"]["rules"].append({
                "type": "field",
                "protocol": ["bittorrent"],  # BT流量直连
                "outboundTag": "direct"
            })

            if proxy == 1:  # 国内网站直连：
                conf["routing"]["rules"].append({
                    "type": "field",
                    "ip": [
                       "geoip:private",
                       "geoip:cn"
                    ],
                    "outboundTag": "direct"
                })
                conf["routing"]["rules"].append({
                    "type": "field",
                    "domain": [
                        "geosite:cn"
                    ],
                    "outboundTag": "direct"
                })
            else:  # gfw
                conf["routing"]["rules"].append({
                    "type": "field",
                    "domain": [
                        "ext:h2y.dat:gfw"
                    ],
                    "outboundTag": "proxy"
                })
                conf["routing"]["rules"].append({
                    "type": "field",
                    "network": "tcp,udp",
                    "outboundTag": "direct"
                })

        with open("/etc/v2rayL/config.json", "w") as f:
            f.write(json.dumps(conf, indent=4))

    def delconf(self, region):
        """
        删除一个配置
        :param region: 配置名
        :return:
        """
        self.conf.pop(region)
        try:
            self.saved_conf['local'].pop(region)
        except KeyError:
            self.saved_conf['subs'].pop(region)
        except:
            raise MyException("配置删除出错，请稍后再试..")

        with open("/etc/v2rayL/ndata", "wb") as jf:
            pickle.dump(self.saved_conf, jf)

    def update(self, flag):
        """
        更新订阅
        :param flag: True, 整体更新, False, 添加
        """
        error_subs = []
        if flag:
            all_subs = []
            for url in self.subs_url:
                # print(url)
                try:
                    ret = requests.get(url[1], timeout=30, headers={'user-agent': 'v2rayL/2.1.3 (GUI)'})
                    if ret.status_code != 200:
                        error_subs.append([url, "无法获取订阅信息，订阅站点访问失败"])
                        raise MyException("无法获取订阅信息，订阅站点访问失败")
                    subs = base64.b64decode(ret.text + "==").decode().strip()
                    all_subs.extend(subs.split("\n"))
                except:
                    pass
                    # raise MyException(e.args[0])
                    # error_subs.append(url)

            for sub in all_subs:
                self.origin.append(sub.split("://"))

            self.saved_conf["subs"] = {}

        else:
            try:
                print(self.subs_url)
                ret = requests.get(self.subs_url, timeout=30)
                if ret.status_code != 200:
                    raise MyException("无法获取订阅信息，订阅站点访问失败")
                all_subs = base64.b64decode(ret.text + "==").decode().strip()
                if "vmess" not in all_subs or "ss" not in all_subs:
                    raise MyException("解析订阅信息失败，请确认链接正确")
                all_subs = all_subs.split("\n")
            except Exception:
                raise MyException("无法获取订阅信息，订阅站点访问失败")

            for sub in all_subs:
                self.origin.append(sub.split("://"))

        for ori in self.origin:
            if ori[0] == "vmess":
                self.b642conf("vmess", 1, ori[1])
            elif ori[0] == "ss":
                self.b642conf("shadowsocks", 1, ori[1])

        self.conf = dict(self.saved_conf['local'], **self.saved_conf['subs'])

        with open("/etc/v2rayL/ndata", "wb") as jf:
            pickle.dump(self.saved_conf, jf)

        return error_subs

    def add_conf_by_uri(self):
        """
        通过分享的连接添加配置
        """
        try:
            op = self.conf_url.split("://")
            if op[0] == "vmess":
                self.b642conf("vmess", 0, op[1])
            elif op[0] == "ss":
                self.b642conf("shadowsocks", 0, op[1])
            else:
                raise MyException("无法解析的链接格式")
        except Exception as e:
            if e.args[0] == "无法解析的链接格式":
                raise MyException("无法解析的链接格式")
            raise MyException("解析失败，请在github提交错误")

        self.conf = dict(self.saved_conf['local'], **self.saved_conf['subs'])

        with open("/etc/v2rayL/ndata", "wb") as jf:
            pickle.dump(self.saved_conf, jf)

    def conf2b64(self, region):
        tmp = dict()
        prot = self.conf[region]['prot']
        for k, v in self.conf[region].items():
            tmp[k] = v
        tmp.pop("prot")
        if prot == "vmess":
            return prot+"://"+base64.b64encode(str(tmp).encode()).decode()
        else:
            prot = "ss"
            return prot+"://"+base64.b64encode("{}:{}@{}:{}".format(tmp["method"],
                                                                       tmp["password"], tmp["add"],
                                                                       tmp["port"]).encode()).decode()+"#"+region


# 异常
class MyException(Exception):
    def __init__(self, *args):
        self.args = args


# if __name__ == '__main__':
#     # s = Sub2Conf("https://sub.qianglie.xyz/subscribe.php?sid=4594&token=TCDWnwMD0rGg")
#     # print(s.conf)
#
#     # s.setconf("1.0x TW-BGP-A 台湾")
#
#     # t = base64.b64decode("ewoidiI6ICIyIiwKInBzIjogIjIzM3YyLmNvbV8xNDIuOTMuNTAuNzgiLAoiYWRkIjogIjE0Mi45My41MC43OCIsCiJwb3J0IjogIjM5Mzk4IiwKImlkIjogIjc1Y2JmYzI0LTZhNjAtNDBmMC05Yjc2LTUyMTlmNTIwYTJlMCIsCiJhaWQiOiAiMjMzIiwKIm5ldCI6ICJrY3AiLAoidHlwZSI6ICJ1dHAiLAoiaG9zdCI6ICIiLAoicGF0aCI6ICIiLAoidGxzIjogIiIKfQo=").decode().strip()
#     # print(t)
#
#     b642conf("ss", "YWVzLTI1Ni1jZmI6NTQxNjAzNDY2QDE0Mi45My41MC43ODo5ODk4#ss")
