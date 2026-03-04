
import math,requests

def haversine(lat1,lon1,lat2,lon2):
    R=3958.8
    lat1,lon1,lat2,lon2=map(math.radians,[float(lat1),float(lon1),float(lat2),float(lon2)])
    dlat=lat2-lat1
    dlon=lon2-lon1
    a=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    return R*c

def geocode(addr):
    url="https://nominatim.openstreetmap.org/search"
    params={"q":addr,"format":"json","limit":1}
    r=requests.get(url,params=params,headers={"User-Agent":"crm"})
    d=r.json()
    if d:
        return float(d[0]["lat"]),float(d[0]["lon"])
    return None,None
