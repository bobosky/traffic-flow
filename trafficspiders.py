#-*-coding:utf-8-*- 
import os
import urllib2
import cookielib
import threading
import time
from coordtrans import Coord
from Multithreading import ThreadPool

'''
交通流量切片下载
'''

class Spider:

    '''
    @url 切片url
    '''
    def Downtile(self,url):
        try:
            cj = cookielib.LWPCookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)
            headers={'User-agent' : 'Mozilla/5.0'}
            req = urllib2.Request(url,None,headers)
            operate = opener.open(req,timeout = 2)
            data = operate.read()
            #date = operate.headers.get('Date')#'Wed, 25 May 2016 07:28:49 GMT'
            return data
        except BaseException, e:
            return None
    
    def Savetile(self,path,filename,tiledata):
        if tiledata == None:
            return
        png = open(path+"\\"+filename,"wb")
        png.write(tiledata)
        png.flush()
        png.close()

    def __init__(self,url,filename,pathdir):
        
        self.pathname = pathdir  # 存放小瓦片
        # 运行状态
        self.status = True  # 正常运行

        tilepath = self.pathname
        tiledata = self.Downtile(url)
        # 异常处理
        if tiledata is None:
            self.status = False
            return
        # 过滤无效数据
        if len(tiledata)<46:
            return
        if not os.path.isfile(tilepath+"\\"+filename):
            print '\n' + url               
            self.Savetile(tilepath,filename,tiledata)        

def Getrange(num_min,num_max):
    num = num_max - num_min + 1
    _list = [ 0 for i in range(num)]
    for i in range(num):
        _list[i] = num_min + i
    return _list

def main():
    '''
    @maprange 地图范围
    @zoom 地图缩放等级
    '''   
    
    maprange = (115.829,117.257,39.358,40.457)
    zoom = 3
    
    # 实例化系统转换类
    CD = Coord()
    # 获取切片索引范围
    indexrange = CD.TileRange(maprange,zoom)
    del CD
    _time = time.localtime(time.time())
    pathdir = os.getcwd() +'\\trafficdata\\tile\\' +'%s_%s_%s_%s_%s'%(_time.tm_year,_time.tm_mon,_time.tm_mday,_time.tm_hour,_time.tm_min)
    if not os.path.exists(pathdir):
        os.makedirs(pathdir)# 创建缓存瓦片目录层

    # 实例化自定义类 threadpool ,10个线程，超时110秒
    threadpool = ThreadPool(10,110) 
    
    x_range = Getrange(indexrange[0],indexrange[1])
    y_range = Getrange(indexrange[2],indexrange[3])        
    for ix in x_range:
        for iy in y_range:
            # 判断任务列表是否过大
            if threadpool.overburden == True:
                time.sleep(10)
            url = "http://gis.bjjtgl.gov.cn:8083/maptile/maptile?v=1.0&t=1&zoom=%s&x=%s&y=%s"%(zoom,ix,iy)                  
            # 切片命名 x_y
            filename = '%s_%s.png'%(ix,iy)
            threadpool.addTask(Spider,(url,filename,pathdir))    

    
if __name__=="__main__":
    '''
    @runcounts 程序运行次数
    @interval 时间间隔s
    '''
    runcounts = 100
    interval = 2 * 60
    
    for runcount in range(runcounts):
        start_time = time.time()
        main()        
        end_time = time.time()
        if int(interval+start_time-end_time)>0:
            time.sleep(int(interval+start_time-end_time))
        
    #提示按回车退出
    raw_input("\nPress <Enter> To Quit!")
