# -*- coding=utf-8 -*-
APP_CONFIG = {
    #'host':'http://api-test.thebeastshop.com',
    'host':'http://114.55.38.62:8080',
    'auth_key': 'Authorization',
    'user':'******',
    'password':'******',
    'authentication':'/app/authentication',
    'detail_url':'/app/product/PROD001016515',
    'order_url':'/app/order',
    "prod":
    {'packs':[
        {"id":None,
         "count":1,
         "spv":{"id":13786}
         }],
       "addressId":1618813,
       "deliveryDate":"2016-12-01",
       "deliveryTimeSlot":None,
       "anonymous":False,
       "useBdayDiscount":False,
       "price":200
    },
    #'cs_host':'http://120.27.240.62:8081',
    'cs_host':'http://114.55.38.62:8081',
    'cs_url_product':'/api/product/getProduct',
    'cs_url_pContent':'/api/product/productContent',
    'cs_code':'******',
    'cs_api_key':'******',
    'cs_data':{
        'accessWay':2,
        'memberId':1962331,
        'productCode':"PROD001016301",

    }
}

WEBSITE_CONFIG = {
    'host':'http://websitetest.thebeastshop.com',
    #'host':'http://10.172.200.64:8080',
    'detail_url': '/item/detail/PROD001016515.htm',
    'order_url':'/app/order/create.htm',
    'user':'******',
    'password':'******',
    'cs_host':'http://120.27.240.62:8081',
    'cs_url':'/api/item/product/detail',
    'cs_code':'******',
    'cs_api_key':'******',
    'cs_data':{
        'accessWay':1,
        'currpage':"1",
        'keyword':"PROD001016301",
        'matchCampaign':True,
        'memberLevel':0,
        'pagenum':"20"
    }
}

