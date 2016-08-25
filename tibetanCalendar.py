#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import configparser
import logging
import datetime
import os

# 参数获取定义ini文件
CONFIG = configparser.ConfigParser()
if os.path.isfile("calendarConfig.ini"):
    CONFIG.read("calendarConfig.ini")
else: # 如配置文件不存在则新建默认配置内容
    iniFile = open("calendarConfig.ini", "w")
    # 追加默认配置文件内容
    iniText = '''# 本程序完全使用文本作为逻辑判断依据,请务必保障Constant中的月&日内容和Year中的月日格式内容完全一致,如出现类似"廿一"和"二十一"这样的不一致将出现错误。\n\n[Constant] #基础常量,多参数以空格分隔\n# 月份列表\nMONTHLIST: 一月 二月 三月 四月 五月 六月 七月 八月 九月 十月 十一月 十二月\n# 日期列表(藏历每月固定三十日)\nDAYLIST: 初一 初二 初三 初四 初五 初六 初七 初八 初九 初十 十一 十二 十三 十四 十五 十六 十七 十八 十九 二十 廿一 廿二 廿三 廿四 廿五 廿六 廿七 廿八 廿九 三十\n\n[Year] #目标年份参数配置,多参数以空格分隔\n# 目标年\nYEAR: 2016\n# 起始日期(公历一月一日元旦所对应的藏历日期)\nSTARTDATE: 十一月廿二\n# 结束日期(公历十二月三十一日所对应的藏历日期)\nENDDATE: 十一月初二\n# 闰月常量(可多个)\nLEAPMONTH: 四月\n# 缺日\nLAKEDAY: 十二月十二 一月初六 二月初一 三月初五 三月廿九 闰四月初二 闰四月廿五 五月廿八 六月二十 七月廿三 八月十七 九月廿一 十月十四\n# 重日(又称闰日)\nDUPDAY: 十二月十九 一月廿二 三月十五 四月初十 六月初六 八月初二 九月廿六 十月三十\n\n[MonthlyHolidays] #每月节日\n初八: 药师佛日\n初十: 莲师荟供日\n十五: 阿弥陀佛节日\n廿五: 空行母荟供日\n三十: 释迦牟尼佛节日\n\n[AnnualHolidas] #每年节日\n一月初八: 一年第一天\n十二月三十: 一年最后一天'''
    try:
        iniFile.write(iniText)
    finally:iniFile.close()
    CONFIG.read("calendarConfig.ini")

# log文件定义
logging.basicConfig(filename="tibetanCalendar.log", level=logging.DEBUG)

# 生成ics文件函数
def makeFile(ICSlist):
    f = open('tibetanCalendar.ics', 'w')
    try:
        for m in ICSlist:
            for n in m:
                f.write(n + '\n')
    finally:f.close()


def tibetanCalendarIni():

    # 月份及日期列表常量
    MONTHLIST = CONFIG.get("Constant", "MONTHLIST").split()
    DAYLIST = CONFIG.get("Constant", "DAYLIST").split()
    # 起始日期
    STARTDATE = CONFIG.get("Year", "STARTDATE")
    # 闰月常量
    LEAPMONTH = CONFIG.get("Year", "LEAPMONTH").split()
    # 实际月份中追加闰月（在同一月份之后增加‘闰＃月’的条目
    if LEAPMONTH != "":
        for leap in LEAPMONTH:
            MONTHLIST.insert(MONTHLIST.index(leap) + 1, '闰' + leap)
    # 缺日及重日常量
    LAKEDAY = CONFIG.get("Year", "LAKEDAY").split()
    DUPDAY = CONFIG.get("Year", "DUPDAY").split()

    newlist = []
    # 整合月日为完整日历
    for month in MONTHLIST:
        for day in DAYLIST:
            date = month + day
            newlist.append(date)
    for lake in LAKEDAY:
        # 删除list中的缺日，低概率可能返回异常
        try:
            newlist.remove(lake)
        except ValueError as e:
            print("缺日:" + lake + "未匹配到")
    for dup in DUPDAY:
        # list中追加重日，低概率可能返回异常
        try:
            newlist.insert(newlist.index(dup), dup)
        except ValueError as e:
            print("重日:" + dup + "未匹配到")

    # Double list方便截取
    templist = newlist * 2

    # 从起始日期截取
    templist = templist[templist.index(STARTDATE):]
    logging.debug("基础藏历日期列表已生成:"+'\n'+str(templist))
    return templist

# 网上copy的公历日期列表生成
def datelist(year):
    start_date = datetime.date(*(year, 1, 1))
    end_date = datetime.date(*(year, 12, 31))
    result = []
    curr_date = start_date
    next_date = curr_date + datetime.timedelta(1)
    while curr_date != end_date:
        result.append(["%04d%02d%02d" % (curr_date.year, curr_date.month, curr_date.day),
                       "%04d%02d%02d" % (next_date.year, next_date.month, next_date.day)])
        curr_date += datetime.timedelta(1)
        next_date += datetime.timedelta(1)
    result.append(["%04d%02d%02d" % (curr_date.year, curr_date.month, curr_date.day),
                   "%04d%02d%02d" % (next_date.year, next_date.month, next_date.day)])
    # result[0]为当前日，对应ics中DTSTART；result[1]为下一日，对应ics中DTEND
    logging.debug("基础公历日期列表已生成:"+"\n"+str(result))
    return result

# 拼合藏历列表和公历列表
def ziplist(GregorianCalendar, TibetanCalendar):
    result = []
    for gc, tc in zip(GregorianCalendar, TibetanCalendar):
        result.append([gc[0], gc[1], tc])
    if CONFIG.get("Year", "ENDDATE") != result[-1][-1]:
        logging.warning("日期匹配异常!请检查配置")
        return "日期匹配异常!"
    else:
        logging.debug("整合日期列表已生成:"+"\n"+str(result))
        return result

# 生成ics文件
def makeICS(ziplist):
    if type(ziplist) is str:
        print(ziplist)
        return ziplist
    ICSHEAD = [["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:TibetanCalendar", "CALSCALE:GREGORIAN", "X-WR-CALNAME:藏历",
                "X-WR-CALDESC:基于iCal的藏历"]]
    eventlist = []
    ICSFOOT = [["END:VCALENDAR", ]]
    id = 0
    for line in ziplist:
        linelist = []
        BEGINEVENT = "BEGIN:VEVENT"
        ENDEVENT = "END:VEVENT"
        UID = "UID:"
        DTSTART = "DTSTART;VALUE=DATE:"
        DTEND = "DTEND;VALUE=DATE:"
        SUMMARY = "SUMMARY:"
        DESCRIPTION = "DESCRIPTION:"
        id += 1
        linelist.append(BEGINEVENT)
        linelist.append(UID + line[0][:4] + "%04d" % (id) + "@huidengzhiguang.com")
        linelist.append(DTSTART + line[0])
        linelist.append(DTEND + line[1])
        linelist.append(SUMMARY + line[2])
        summarysplit = line[2].split('月')
        holiday = ""
        ANNUALHOLIDAYLIST = CONFIG["AnnualHolidas"]
        MONTHLYHOLIDAYLIST = CONFIG["MonthlyHolidays"]
        if line[2] in ANNUALHOLIDAYLIST:
            if len(holiday) > 0:holiday += "\\n"
            holiday += ANNUALHOLIDAYLIST[line[2]]
        if summarysplit[1] in MONTHLYHOLIDAYLIST:
            if len(holiday) > 0: holiday += "\\n"
            holiday += MONTHLYHOLIDAYLIST[summarysplit[1]]
        if len(holiday) > 0: linelist.append(DESCRIPTION + holiday)
        linelist.append(ENDEVENT)
        eventlist.append(linelist)
        logging.debug(line[0]+"的ics已完成:\n"+str(linelist))
    result = ICSHEAD + eventlist + ICSFOOT
    logging.debug("ics整合完成")
    return result

try:
    YEAR = CONFIG.getint("Year", "YEAR")
    makeFile(makeICS(ziplist(datelist(YEAR), tibetanCalendarIni())))
except ValueError as e:
    print("YEAR参数异常,请检查ini文件配置")