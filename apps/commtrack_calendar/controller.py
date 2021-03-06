import eventCalBase
from resources.models import *
import calendar



class CalendarController(object):
    """Controller object for calendar"""
    def __init__(self, day=1,q=0):
        """owner - owner of this calendar, day - day to shown"""
        calendar.setfirstweekday(calendar.SUNDAY)
        self.area = q
        self.day = day
        self.curr = None
        self.db_cal = None
        self.db_events = None

## database related operation (i.e. operation will sync with DB
    def load(self, year, month):
        """load calendar with data from database"""
        
        temp = filter_samples(0,month,year,0)
        if temp:    # either 1 record or no record , check models.py
            self.db_cal = temp[0]
            
            if self.area == 0:
                self.db_events = filter_samples(0,month,year,self.area)
            else:
                self.db_events = filter_samples(0,month,year,self.area)
            self.curr = eventCalBase.monthCalendar(self, year, month)
#put events to map a month
            for db_e in self.db_events:              
                e = eventCalBase.event(db_e.id, db_e.name,db_e.date_added, db_e.facility)
                self.curr.addEvent(e, db_e.date_added.day)
        else:
            self.curr = eventCalBase.monthCalendar(None,
                    year, month)


## functions used by template
    def next(self):
        """return a tuple that contains next year and month"""
        y = self.curr.year
        m = self.curr.month
        if m == 12:
            m = 1
            y += 1
        else:
            m += 1
        return (y,m)
        
    def prev(self):
        """return a tuple that contains previous year and month"""
        y = self.curr.year
        m = self.curr.month
        if m == 1:
            m = 12
            y -= 1
        else:
            m -= 1
        return (y,m)
        
    def getWeekHeader(self):
        """return a list of week header"""
        return calendar.weekheader(2).split()

    def getMonthHeader(self):
        """return a tuple that contains abbv. month name and 4 digit year"""
        return self.curr.getDate(1).strftime("%b"), self.curr.year
#put counts on the calendar
    def getMonthCalendar(self):
        """return a matrix similar to calendar.monthCalendar().  Except
           the element is replaced by (day, event exist,count)"""
        res = []
        for dayline in calendar.monthcalendar(self.curr.year, self.curr.month):
            res_line = []
            for day in dayline:
                data = False
                total = 0
                abnormal = 0
                if day in self.curr.events:
                    data = True
                    if self.area == 0:
                        a = filter_samples(day,self.curr.month,self.curr.year,0)
                    else:
                        a = filter_samples(day,self.curr.month,self.curr.year,self.area)
                    total = a.count()
#                    qu = Resource.objects.filter(facility__location__type = 'Tanzania')
#                    print ' ---magic---'
#                    print qu
#wait for abnormal range fixing issue
#Write a function here that assign number to abnormal due to number of samples in a day that are abnormal
#like abnormal vals to be retured shud be
#1 for 0 abnormal range
#2 for 1 abnormal range
#3 for more than 1 banormal range
#actually the thing abnornal assigns td name to be used by css to put color
                    abnormal = 1
                res_line.append((day, data, total,abnormal))
            res.append(res_line)
        return res
        
    def getDailyEvents(self):
        """return list of events for the day"""
        return self.curr.getDailyEvents(self.day)

    def hasDailyEvents(self):
        """return list of events for the day"""
        return len(self.curr.getDailyEvents(self.day)) > 0

    def getDayName(self):
        result = 'th'
        if self.day % 10 == 1 and self.day != 11:
            result = 'st'
        elif self.day % 10 == 2 and self.day != 12:
            result = 'nd'
        elif self.day % 10 == 3 and self.day != 13:
            result = 'rd'
        return result
#
#here is the database interaction
#
def filter_samples(day,month,year,area):
    if area == 0 and month != 0 and day != 0:
        a = Resource.objects.filter(date_added__day = day,
                    date_added__month = month,
                    date_added__year = year)
    elif area != 0 and day != 0:
        a = Resource.objects.filter(date_added__day = day,
                            date_added__month = month,
                            date_added__year = year,
                            facility__id = area
                            )
    elif day == 0 and area == 0:
        a = Resource.objects.filter(date_added__year=year, date_added__month=month)
    elif day ==0 and area != 0:
        b = Resource.objects.filter(date_added__year=year, date_added__month=month)
        a = b.filter(facility__id = area)
    return a