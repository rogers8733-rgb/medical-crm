
import math

def haversine(lat1,lon1,lat2,lon2):
    R=3958.8
    lat1,lon1,lat2,lon2=map(math.radians,[float(lat1),float(lon1),float(lat2),float(lon2)])
    dlat=lat2-lat1
    dlon=lon2-lon1
    a=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    return R*c

def optimize(start_lat,start_lon,points):
    route=[]
    current=(float(start_lat),float(start_lon))
    remaining=points[:]

    while remaining:
        nearest=min(remaining,key=lambda p:haversine(current[0],current[1],p["latitude"],p["longitude"]))
        route.append(nearest)
        current=(nearest["latitude"],nearest["longitude"])
        remaining.remove(nearest)

    return route
