
import math,requests

def haversine(lat1,lon1,lat2,lon2):
    R=3958.8
    lat1,lon1,lat2,lon2=map(math.radians,[float(lat1),float(lon1),float(lat2),float(lon2)])
    dlat=lat2-lat1
    dlon=lon2-lon1
    a=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    return R*c

def geocode_address(address):
    url="https://nominatim.openstreetmap.org/search"
    params={"q":address,"format":"json","limit":1}
    headers={"User-Agent":"crm-app"}

    r=requests.get(url,params=params,headers=headers)
    data=r.json()

    if data:
        return data[0]["lat"],data[0]["lon"]

    return None,None
