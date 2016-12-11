Restful api接口型压力测试
====
使用gevent进行压力测试


依赖库
====
gevent
matplotlib
urllib
urllib2

运行方式
====
python demo.py


一个简单的例子
====

#继承Capability类导入压测时需要使用到的一些属性
Capability.__init__(self,increment,final)



#使用装饰器把目标函数包装成可并发的函数
    @Capability.concurrent()
    def run_detail(self):
        url = 'https://www.baidu.com/'
        request = urllib2.Request(url)
        request.add_header("Platform","python")
        print "Visit:%s" % url
#使用with语法糖计算接口请求消耗的时间
        with self:
            response = urllib2.urlopen(request).read()

#开始运行
web = Website(1,3)  
web.run_detail()  


#下面是程序的输出:  
Visit:https://www.baidu.com/  
当前并发：1  
最小响应时间:0.173840  
最大响应时间:0.173840  
平均响应时间（RT）:0.173840  
并发总时间:1.015974  
并发总平均时间:1.015974  
最小TPS:1  
最大TPS:1  
平均TPS:1.000000  
错误率:0.000000  

Visit:https://www.baidu.com/  
Visit:https://www.baidu.com/  
当前并发：2  
最小响应时间:0.047717  
最大响应时间:0.051873  
平均响应时间（RT）:0.049795  
并发总时间:1.003607  
并发总平均时间:0.501804  
最小TPS:2  
最大TPS:2  
平均TPS:2.000000  
错误率:0.000000  

Visit:https://www.baidu.com/  
Visit:https://www.baidu.com/  
Visit:https://www.baidu.com/  
当前并发：3  
最小响应时间:0.047715  
最大响应时间:0.058399  
平均响应时间（RT）:0.053281  
并发总时间:1.006875  
并发总平均时间:0.335625  
最小TPS:3  
最大TPS:3  
平均TPS:3.000000  
错误率:0.000000  

![image](https://github.com/leoche666/Web-Pressure-test/blob/master/img-folder/image1.png)

![image](https://github.com/leoche666/Web-Pressure-test/blob/master/img-folder/image2.png)

代码详细说明
====
http://note.youdao.com/noteshare?id=4e717678d9dd6f47d974e6aa090ec4df

http://note.youdao.com/noteshare?id=282fb6d468e33970b3aa151bc7176d2f
