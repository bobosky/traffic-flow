#-*-coding:utf-8-*- 
import math

class Coord:
       '''
       坐标系统转换

       '''
       def Resolution(self, zoom ):
              " 缩放级别的分辨率(meters/pixel)"
              return self.initialResolution / (2**(17-zoom))
       
       def Origin(self,tile_x,tile_y,zoom):
              " 计算瓦片索引(tile_x,tile_y)左上角Mercator EPSG:900913"
              
              # google map
              x_min = -20037508.3427892
              y_max = 20037508.3427892
              
              
              mx = x_min+tile_x*self.tileSize*self.Resolution(zoom)
              my = y_max-tile_y*self.tileSize*self.Resolution(zoom)
              return mx,my

       def pixeltoxy(self,px,py,tile_x,tile_y,zoom):
              "切片索引（tile_x,tile_y），像素坐标（px,py)转Mercator EPSG:900913"
              ox,oy=self.Origin(tile_x,tile_y,zoom)
              mx = ox + px *self.Resolution(zoom)+self.Resolution(zoom)*0.5
              my = oy - py *self.Resolution(zoom)-self.Resolution(zoom)*0.5
              return mx,my
       
       def out_of_china(self,lng, lat):
              """
              判断是否在国内，不在国内不做偏移
              :param lng:
              :param lat:
              :return:
              """
              if lng < 72.004 or lng > 137.8347:
                     return True
              if lat < 0.8293 or lat > 55.8271:
                     return True
              return False
       
       def wgs84togcj02(self,lng, lat):
              
              """
              WGS84转GCJ02(火星坐标系)
              :param lng:WGS84坐标系的经度
              :param lat:WGS84坐标系的纬度
              :return:
              """
              pi = math.pi
              ee = 0.00669342162296594323  # 扁率
              a = 6378245.0  # 长半轴 
              if self.out_of_china(lng, lat):  # 判断是否在国内
                     return lng, lat
              dlat = self._transformlat(lng - 105.0, lat - 35.0)
              dlng = self._transformlng(lng - 105.0, lat - 35.0)
              radlat = lat / 180.0 * pi
              magic = math.sin(radlat)
              magic = 1 - ee * magic * magic
              sqrtmagic = math.sqrt(magic)
              dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
              dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
              mglat = lat + dlat
              mglng = lng + dlng
              return mglng,mglat
       
       def gcj02towgs84(self,lng,lat):
              """
              GCJ02(火星坐标系)转GPS84
              :param lng:火星坐标系的经度
              :param lat:火星坐标系纬度
              :return:
              """
              pi = math.pi
              ee = 0.00669342162296594323  # 扁率
              a = 6378245.0  # 长半轴 
              if self.out_of_china(lng, lat):
                     return lng, lat
              dlat = self._transformlat(lng - 105.0, lat - 35.0)
              dlng = self._transformlng(lng - 105.0, lat - 35.0)
              radlat = lat / 180.0 * pi
              magic = math.sin(radlat)
              magic = 1 - ee * magic * magic
              sqrtmagic = math.sqrt(magic)
              dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
              dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
              mglat = lat + dlat
              mglng = lng + dlng
              return lng * 2 - mglng, lat * 2 - mglat

       def _transformlat(self,lng, lat):
              pi = math.pi
              ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
                     0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
              ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
                     math.sin(2.0 * lng * pi)) * 2.0 / 3.0
              ret += (20.0 * math.sin(lat * pi) + 40.0 *
                     math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
              ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
                     math.sin(lat * pi / 30.0)) * 2.0 / 3.0
              return ret

       def _transformlng(self,lng, lat):
              pi = math.pi
              ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
                     0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
              ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
                     math.sin(2.0 * lng * pi)) * 2.0 / 3.0
              ret += (20.0 * math.sin(lng * pi) + 40.0 *
                     math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
              ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
                     math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
              return ret

       def LatLonToMeters(self, lng, lat ):
              "(lng,lat) in WGS84 (X,Y) to Mercator EPSG:900913"
              mx = lng * self.originShift / 180.0
              my = math.log( math.tan((90 + lat) * math.pi / 360.0 )) / (math.pi / 180.0)

              my = my * self.originShift / 180.0
              return mx, my

       def MetersToLatLon(self, mx, my ):
              " XY point Mercator EPSG:900913 to lon/lat  WGS84"
              lon = (mx / self.originShift) * 180.0
              lat = (my / self.originShift) * 180.0

              lat = 180 / math.pi * (2 * math.atan( math.exp( lat * math.pi / 180.0)) - math.pi / 2.0)
              return lon,lat

       def GetTile(self,lon,lat,zoom):
              "input wgs84坐标（lon,lat) return 切片索引"
              # wgs84转web墨卡托
              mx,my = self.LatLonToMeters(lon,lat)
              ox,oy = self.Origin(0,0,zoom)
              size = self.Resolution(zoom)*self.tileSize
              xi = int((mx-ox)/size)
              yi = int((oy-my)/size)
              return xi,yi
       def TileRange(self,maprange,zoom):
              "input wgs84 (lon_min,lon_max,lat_min,lat_max) and zoom return (xmin,xmax,ymin,ymax)"
              lon_min,lon_max,lat_min,lat_max = maprange[0],maprange[1],maprange[2],maprange[3]
              xmin,ymin = self.GetTile(lon_min,lat_max,zoom)
              xmax,ymax = self.GetTile(lon_max,lat_min,zoom)
              return xmin,xmax,ymin,ymax
       
       def __init__(self, tileSize=256):
              # 瓦片分辨率
              self.tileSize = tileSize
              # 初始瓦片尺寸
              self.initialResolution = 2 * math.pi * 6378137 / self.tileSize
              self.originShift = 2 * math.pi * 6378137 / 2.0
              
