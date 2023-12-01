import numpy as np
def degrees2clock(angle_deg):
    #Convert degrees into hours and minutes (o'clocks)
    a = angle_deg
    if a<0:
        a+=360
    hour = np.floor(a * 12/360.0)
    minutes = a*12/360.0 - hour
    if hour==0:
        hour = 12.0
    minutes = minutes*60
    return "%i:%s"%(hour,("%i"%minutes).zfill(2))