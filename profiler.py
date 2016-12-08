# -*- coding=utf-8 -*-
import time
from functools import wraps
import urllib2
TIMEOUT = 60 * 3
WAIT_NEXT_SEC = 2
SEM = 1
INSPECT_TIME = 1
CONCURRENCY = 5755

class Line(object):
    def __init__(self,fig,ax,xdata,ydata,dt=0.01,xInterval=1):
        from matplotlib.lines import Line2D
        self.fig, self.ax = fig,ax
        self.dt = dt

        self.xdata = xdata
        self.ydata = ydata
        self.xInterval = xInterval

        #initalize the Line2D which will paint in the figure
        self.line = Line2D(xdata,ydata,linewidth=1)
        #put the line 2d into the figure
        self.ax.add_line(self.line)

        #update the xticks and the yticks
        self.update_xaxis(self.ax)
        self.update_yaxis(self.ax)

    def update_xaxis(self,ax):
        #ax.xaxis.set_ticks([])
        ax.set_xlim(self.xdata[0],self.xdata[-1])
        #ax.xaxis.set_ticks(np.arange(self.xdata[0],self.xdata[-1], self.xInterval))
        #ax.xaxis.set_ticklabels([xtick for xtick in self.xdata])
        #plt.xticks(rotation=270)
        self.ax.figure.canvas.draw()

    def update_yaxis(self,ax):
        ax.set_ylim(min(self.ydata),max(self.ydata))
        ax.figure.canvas.draw()

class ProfSemaphore(object):
    def __init__(self,counter=0):
        self.couter = counter

    @property
    def Couter(self):
        return self.couter

    @Couter.setter
    def Couter(self,couter):
        self.couter = couter

    def acquire(self):
        self.couter -= 1

    def release(self):
        self.couter += 1

    def __enter__(self):
        self.couter -= 1

    def __exit__(self, *args):
        self.couter += 1

#指令耗时计算
class Elapse(object):
    def __init__(self,verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        if self.verbose:
            print 'elapsed time: %f s' % self.secs

class Capability(Elapse):
    #增量
    increment = 0
    #最终量
    final = 0
    #并发数
    ct = 0
    #每秒事务数
    tps = 0
    #平均响应时间
    rt = 0
    #并发开始时间
    crt_stime = 0
    #并发结束时间
    crt_etime = 0
    #并发总时间
    ttime = 0
    #并发总平均时间
    trt = 0
    #TPS列表
    ltps = []
    #RT列表
    lrt = []
    #错误列表
    lerr = []
    #上次的ltps的数量
    last_count_tps = 0
    #绘图数据
    data = []
    #并发资源数
    tgtSem = ProfSemaphore()

    def __init__(self,increment,final):
        Elapse.__init__(self,False)
        #增量
        Capability.increment = increment
        #最终量
        Capability.final = final

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.lrt.append(self.secs)
        if self.verbose:
            print 'elapsed time: %f s' % self.secs

    def local_time(self):
        return time.time()

    @classmethod
    def _reset(self):
        self.ct = 0
        self.tps = 0
        self.rt = 0
        self.crt_stime = 0
        self.crt_etime = 0
        self.ttime = 0
        self.trt = 0
        self.ltps = []
        self.lrt = []
        self.lerr = []
        self.last_count_tps = 0

    @classmethod
    def _calculate_tps(cls,*args,**kwargs):
        import gevent
        while cls.tgtSem.Couter:
            gevent.sleep(INSPECT_TIME)
            cls.ltps.append(len(cls.lrt) - cls.last_count_tps)
            cls.last_count_tps = len(cls.lrt)
            gevent.sleep(0)

    @classmethod
    def _statistics(cls,*args,**kwargs):
        cls.ct, = args
        rt_min = min(cls.lrt)
        rt_max = max(cls.lrt)
        cls.rt = reduce(lambda x,y:x+y,cls.lrt) / len(cls.lrt)
        tps_min = min(cls.ltps)
        tps_max = max(cls.ltps)
        cls.tps = reduce(lambda x,y:x+y,cls.ltps) / len(cls.ltps)
        terr = (len(cls.lerr) / float(cls.ct))
        print "当前并发：%d" % cls.ct
        print "最小响应时间:%f" % rt_min
        print "最大响应时间:%f" % rt_max
        print "平均响应时间（RT）:%f" % cls.rt
        print "并发总时间:%f" % cls.ttime
        print "并发总平均时间:%f" % cls.trt
        print "最小TPS:%d" % tps_min
        print "最大TPS:%d" % tps_max
        print "平均TPS:%f" % cls.tps
        print "错误率:%f" % terr
        print
        cls.data.append((cls.ct,rt_min,rt_max,cls.rt,cls.ttime,
                          cls.trt,tps_min,tps_max,cls.tps,terr))

    @classmethod
    def _target(cls,func,i):
        @wraps(func)
        def inner(*args,**kwargs):
            try:
                setattr(cls,'__crt_id__',i)
                func(*args,**kwargs)
            except Exception,ex:
                cls.lerr.append(ex)
                print ex
            finally:
                cls.tgtSem.acquire()
        return inner

    @classmethod
    def concurrent(cls):
        def outter(func):
            import gevent
            from gevent import monkey
            monkey.patch_all()
            from gevent.pool import Pool
            pool = Pool(CONCURRENCY)

            def run(count,target,*args,**kwargs):
                #设置并发资源数
                cls.tgtSem.Couter = count
                #准备卵开始就绪并发
                [pool.spawn(cls._target(target,i),*args,**kwargs) for i in range(count)]
                pool.spawn(cls._calculate_tps,)
                #计算并发总时间
                cls.crt_stime = time.time()
                pool.join(timeout=TIMEOUT)
                cls.crt_etime = time.time()
                cls.ttime = cls.crt_etime - cls.crt_stime
                #计算平均并发时间
                cls.trt = cls.ttime / count
                #统计各项性能指标
                cls._statistics(count)
                #重置各项指标
                cls._reset()
                #等待一段时间间隔开始下次增量并发
                gevent.sleep(WAIT_NEXT_SEC)

            @wraps(func)
            def inner(*args, **kwargs):
                current = 0
                while True:
                    if current >= cls.final:
                        break
                    else:
                        current = current + cls.increment
                        run(current,func,*args,**kwargs)
                cls.draw()
            return inner
        return outter

    def threshold(self):
        assert self.increment == self.final
        final = self.final -1
        @self.__class__.concurrent()
        def inner():
            request = urllib2.Request("http://www.google.com/")
            #系统函数栈切换到最后一个计算下时间，即取了value-1个并发量的切换时间近似value个并发量的切换量的时间
            if self.__class__.__crt_id__ == final:
                crt_etime = time.time()
                print "elapse time {} s...".format(crt_etime - self.__class__.crt_stime)
            with self:
                response = urllib2.urlopen(request).read()
        return inner()


    @classmethod
    def draw(self):
        import matplotlib.pyplot as plt
        import matplotlib as mpl
        #the style of matplotlib.pyplot
        plt.style.use('ggplot')
        #用来正常显示负号
        mpl.rcParams['axes.unicode_minus'] = False
        #设置坐标轴刻度显示大小
        mpl.rc('xtick', labelsize=12)
        mpl.rc('ytick', labelsize=12)

        #the alpha of the line 2d
        ALPHA = .8

        data = zip(*self.data)
        fig1 = plt.figure(1)
        ax211 = fig1.add_subplot(211)
        ax211.set_ylabel('Time/s')
        line_min_rt = Line(fig1,ax211,xdata=data[0],ydata=data[1])
        line_min_rt.line.set_color('#00FF7F')
        line_max_rt = Line(fig1,ax211,xdata=data[0],ydata=data[2])
        line_max_rt.line.set_color('#4169E1')
        line_agv_rt = Line(fig1,ax211,xdata=data[0],ydata=data[3])
        line_agv_rt.line.set_color('#FFC0CB')
        line_agv_rt.line.set_linewidth(2.5)
        plt.legend([line_min_rt.line, line_max_rt.line,line_agv_rt.line],
                   ['MIN_RT','MAX_RT','RT'])
        plt.title('Response time')

        ax212 = fig1.add_subplot(212)
        ax212.set_ylabel('Concurrent total time/s')
        line_tot_rt = Line(fig1,ax212,xdata=data[0],ydata=data[4])
        line_tot_rt.line.set_color('#FFC0CB')
        line_tot_rt.line.set_linewidth(2.5)

        ax2122 = ax212.twinx()
        ax2122.set_ylabel('Concurrent avg time/s')
        line_tot_agv = Line(fig1,ax2122,xdata=data[0],ydata=data[5])
        line_tot_agv.line.set_color('#00FF7F')
        plt.title('Concurrent time')
        plt.legend([line_tot_rt.line,line_tot_agv.line],['Concurrent total time','Concurrent avg time'])

        fig2 = plt.figure(2)
        ax111 = fig2.add_subplot(111)
        ax111.set_ylabel('TPS')
        line_min_tps = Line(fig2,ax111,xdata=data[0],ydata=data[6])
        line_min_tps.line.set_color('#00FF7F')
        line_max_tps = Line(fig2,ax111,xdata=data[0],ydata=data[7])
        line_max_tps.line.set_color('#4169E1')
        line_avg_tps = Line(fig2,ax111,xdata=data[0],ydata=data[8])
        line_avg_tps.line.set_color('#FFC0CB')
        line_avg_tps.line.set_linewidth(2.5)
        plt.title('Transactions Per Second')
        plt.legend([line_min_tps.line,line_max_tps.line,line_avg_tps.line],['MIN_TPS','MAX_TPS','TPS'])
        plt.show()