# -*- coding=utf-8 -*-
import urllib,urllib2
from urllib import quote
import json
from settings import APP_CONFIG,WEBSITE_CONFIG
from profiler import Capability
import hashlib

class Website(Capability):
    def __init__(self,increment,final):
        Capability.__init__(self,increment,final)
    
    #测试官网商品详情页压测
    @Capability.concurrent()
    def run_detail(self):
        url = WEBSITE_CONFIG['host'] + WEBSITE_CONFIG['detail_url']
        request = urllib2.Request(url)
        print "Visit:%s" % url
        with self:
            response = urllib2.urlopen(request).read()

    #接口数据准备
    def prepare_cs_data(self):
        TIMESTAMP = str(int(self.local_time() * 1000))
        DATA = json.dumps(WEBSITE_CONFIG['cs_data'])
        unsignStr = "CODE=" + WEBSITE_CONFIG['cs_code'] + "&DATA=" + DATA + "&TIMESTAMP=" + TIMESTAMP

        m = hashlib.md5()
        m.update(unsignStr + WEBSITE_CONFIG['cs_api_key'])
        SIGN = m.hexdigest()

        url = WEBSITE_CONFIG['cs_host'] + WEBSITE_CONFIG['cs_url'] + "?CODE={0}&DATA={1}&SIGN={2}&TIMESTAMP={3}"
        self.cs_url = url.format(WEBSITE_CONFIG['cs_code'],quote(DATA),SIGN,TIMESTAMP)
        print self.cs_url
    
    #服务器Chanel Service接口压测
    @Capability.concurrent()
    def run_cs(self):
        request = urllib2.Request(self.cs_url)
        with self:
            response = urllib2.urlopen(request).read()


class App(Capability):
    def __init__(self,increment,final):
        Capability.__init__(self,increment,final)
    
    #app登录获取token
    def login(self):
        url = APP_CONFIG['host'] + APP_CONFIG['authentication']
        data = {"principal":APP_CONFIG['user'],
                "credential":APP_CONFIG['password'],
                "authType":"MOBILE",
                }
        request = urllib2.Request(url,data=json.dumps(data))
        request.add_header("Content-Type","application/json")
        request.add_header("Platform","ios")

        sock = urllib2.urlopen(request)
        rspData = json.loads(sock.read())
        self.auth_value = rspData[u'data'][u'id'].encode('utf-8')
        print "log in successfully,and token is : %s" % self.auth_value

    #app商品详情页压测
    @Capability.concurrent()
    def run_detail(self):
        url = APP_CONFIG['host'] + APP_CONFIG['detail_url']
        request = urllib2.Request(url)
        request.add_header("Platform","python")
        print "Visit:%s" % url
        with self:
            response = urllib2.urlopen(request).read()
        print response
    
    #app下订单接口压测
    @Capability.concurrent()
    def run_order(self):
        url = APP_CONFIG['host'] + APP_CONFIG['order_url']
        request = urllib2.Request(url,data=json.dumps(APP_CONFIG['prod']))
        request.add_header("Content-Type","application/json")
        request.add_header("Platform","python")
        request.add_header(APP_CONFIG['auth_key'],self.auth_value)
        print "Visit:%s" % url
        with self:
            response = urllib2.urlopen(request).read()
    
    #接口数据准备
    def prepare_cs_data(self):
        TIMESTAMP = str(int(self.local_time() * 1000))
        DATA = json.dumps(APP_CONFIG['cs_data'])
        unsignStr = "CODE=" + APP_CONFIG['cs_code'] + "&DATA=" + DATA + "&TIMESTAMP=" + TIMESTAMP

        m = hashlib.md5()
        m.update(unsignStr + APP_CONFIG['cs_api_key'])
        SIGN = m.hexdigest()

        cs_url_product = APP_CONFIG['cs_host'] + APP_CONFIG['cs_url_product'] + "?CODE={0}&DATA={1}&SIGN={2}&TIMESTAMP={3}"
        cs_url_pContent = APP_CONFIG['cs_host'] + APP_CONFIG['cs_url_pContent'] + "?CODE={0}&DATA={1}&SIGN={2}&TIMESTAMP={3}"
        self.cs_url_product = cs_url_product.format(APP_CONFIG['cs_code'],quote(DATA),SIGN,TIMESTAMP)
        self.cs_url_pContent = cs_url_pContent.format(APP_CONFIG['cs_code'],quote(DATA),SIGN,TIMESTAMP)
        print self.cs_url_product
        print self.cs_url_pContent
    
    #app服务器Chanel Service接口压测
    @Capability.concurrent()
    def run_cs_product(self):
        request_product = urllib2.Request(self.cs_url_product)
        request_content = urllib2.Request(self.cs_url_pContent)
        with self:
            product = urllib2.urlopen(request_product).read()
            content = urllib2.urlopen(request_content).read()


if __name__ == '__main__':
    #web = Website(1,1)
    #web.threshold()
    #web.prepare_cs_data()
    #web.run_cs()
    app = App(1,10)
    #app.login()
    #app.run_detail()
    #app.run_order()
    app.prepare_cs_data()
    app.run_cs_product()
