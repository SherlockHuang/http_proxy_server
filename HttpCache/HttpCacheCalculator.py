__author__ = 'PsCool'
from HttpProcess import HttpPacketUtil
import HttpCacheComm
import time
import sys

def cal_received_age(date_value=sys.maxint, age_value=0):
    now_t = time.mktime(time.gmtime())
    interval = now_t - date_value

    return max(interval, age_value)

def cal_current_age(received_age, response_t):
    now_t = time.mktime(time.gmtime())
    resident_t = now_t - response_t

    return received_age + resident_t

def cal_freshness_lifetime(max_age_value=-1, expires_value=-1, date_value=sys.maxint, last_modified_value=sys.maxint):
    if max_age_value > 0:
        return max_age_value

    if expires_value - date_value > 0:
        return expires_value - date_value

    now_t = time.mktime(time.gmtime())
    if now_t - last_modified_value > 0:
        return (now_t - last_modified_value) * 0.1

    return HttpCacheComm.TTL

