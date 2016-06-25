#-*-coding:utf-8-*-
import os
import PIL.Image as Image
import re
import threading
from coordtrans import Coord

'''
瓦片拼接
'''

class Stitched:
    def Getfile(self,dirs):
        reg = r'\d{4}_\d{1,2}_\d{1,2}_\d{1,2}_\d{1,2}$'
        rec = re.compile(reg)
        path_list = list()
        for _dir in dirs:        
            p = re.findall(rec,_dir)
            if len(p) >0:
                path_list.append(p[0])
        return path_list
    
    def Tilepiece(self,tile,name):
        '''
        @tilepath 切片路径
        @name 切片下载时间 即文件目录名
        wsize 图片宽度
        hsize 图片高度
        '''
        #imagename = self.imgpath+'\\'+name+'\\'+'%s_%s_%s_%s.png'%(self.tileindex[0],self.tileindex[1],self.tileindex[2],self.tileindex[3])
        imagename = self.imgpath+'\\'+name + '.png'
        if os.path.isfile(imagename):
            print name+'is existing !'
            return
        pi = 256
        wsize = (self.tileindex[1]-self.tileindex[0]+1)*pi
        hsize = (self.tileindex[3]-self.tileindex[2]+1)*pi
        toimage = Image.new('RGBA',(wsize,hsize),None)
        x_range = self.Get_range(self.tileindex[0],self.tileindex[1])
        y_range = self.Get_range(self.tileindex[2],self.tileindex[3])
        for i in x_range:# 横
            for j in y_range:# 竖
                fname = '%s_%s.png'%(i,j)
                #print fname
                if not os.path.isfile(tile + '\\' + fname):  #文件是否存在
                    continue
                fromimage = Image.open(tile + '\\' + fname)
                toimage.paste(fromimage,((i-self.tileindex[0])*pi,(j-self.tileindex[2])*pi))
                del fromimage
        toimage.save(imagename)
        del toimage
        print name
        print u' 瓦片拼接完成！'

    def Get_range(self,num_min,num_max):
        num = num_max-num_min+1
        _list = [ 0 for i in range(num)]
        for i in range(num):
            _list[i] = num_min+i
        return _list

    def __init__(self,tileindex,tilepath,imgpath):
        self.tileindex = tileindex
        self.tilepath = tilepath
        self.imgpath = imgpath
        # 获取各时间切片路径
        pathlist = self.Getfile(os.listdir(self.tilepath))
        print u' 开始瓦片拼接'
        for name in pathlist:
            self.Tilepiece(self.tilepath+'\\'+name,name)

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
    index = CD.TileRange(maprange,zoom)
    del CD
    # 切片路径
    tilepath = os.getcwd()+'\\trafficdata\\tile'
    # 拼接后路径
    imgpath = os.getcwd()+'\\trafficdata\\data'
    if not os.path.exists(imgpath):
        os.makedirs(imgpath)
    Stitched(index,tilepath,imgpath)

if __name__=="__main__":
    main()
    #提示按回车退出
    raw_input("\n Press <Enter> To Quit!")       
