import Utils
import numpy
import math
import datetime


def Localization(img1, img2, img3):
    img1Data, img2Data, img3Data = Utils.getData(img1, img2, img3)
    altitudeAnglesCam = [img1Data.altitudeAngle, img2Data.altitudeAngle, img3Data.altitudeAngle]
    azimuthAngles = [img1Data.azimuthAngle, img2Data.azimuthAngle, img3Data.azimuthAngle]

    rho1, rho2, rho3, rho4 = Utils.getRho(altitudeAnglesCam, azimuthAngles)
    alpha = math.atan2(rho1 - rho3, rho4 - rho2)
    lat = math.atan(rho1 * math.cos(alpha) + rho2 * math.sin(alpha))
    hourPart = (math.degrees(numpy.mean(altitudeAnglesCam)) + 90) / 180
    longitude, day = getDayNumber(altitudeAnglesCam, azimuthAngles, lat)
    print math.degrees(lat), math.degrees(longitude), day.date(), hourPart
    return math.degrees(lat), math.degrees(longitude), day.date(), hourPart


def getDayNumber(altitudes, azimuths, lat):
    DEL_M = math.radians(23.45)
    N0 = 284
    day = datetime.datetime(2017, 1, 1)
    count = 0
    dayAvg = 0
    h = 0
    for i in range(0, len(altitudes)):
        roots = numpy.roots([1, -2 * math.sin(lat), math.pow(math.cos(lat), 2) * (
            math.pow(math.cos(altitudes[i]) * math.sin(azimuths[i]), 2) - 1) + math.pow(math.sin(altitudes[i]), 2)])
        for j in roots:
            print j
            if math.fabs(j) > 1:
                continue
            angle = math.asin(j)
            # angle = math.radians(math.fabs(j*90))
            if math.fabs(angle) > DEL_M:
                continue
            a = 365 / (2 * math.pi)
            a *= math.asin(angle / DEL_M)
            a -= N0
            dayAvg += a
            count += 1
            h += math.asin(math.cos(altitudes[i]) * math.sin(azimuths[i]) / math.cos(angle))
    if count == 0:
        print "NO VALUES"
        return 0.9, day
    return h / count, day + datetime.timedelta(days=math.ceil(dayAvg / count))
