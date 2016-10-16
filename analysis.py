# http://docs.aws.amazon.com/mobileanalytics/latest/ug/json-export-schema.html
import json
import aws_mobile_analytics_data_parser as aws_madp
import datetime
from datetime import date
import pprint
pp = pprint.PrettyPrinter(indent=4)

def pretty(var):
    pp.pprint(var)

def jpretty(d):
    return json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '))

def get_data_from_cache():
    with open('data.json') as data_file:    
        data = json.load(data_file)
	return data

def bucket_events(data):
    events = {}
    for d in data:
        if d['event_type'] not in events:
            events[d['event_type']] = []
        events[d['event_type']].append(d)
    return events

# note, not currently used but can be used for axis labels by changing 
# parameter event timestamp to date_obj
def formatted_date_str_for_event_time_stamp(event_timestamp):
    datetime_obj = datetime.datetime.fromtimestamp(event_timestamp / 1000)

    year = '{:02d}'.format(datetime_obj.year)
    month = '{:02d}'.format(datetime_obj.month)
    day = '{:02d}'.format(datetime_obj.day)

    date_str = year + "." + month + "." + day
    return date_str

# modifies in place
def add_blank_days_to_bucketed_by_day(bucketed_by_day):
    sorted_keys = sorted(bucketed_by_day.keys())
    start = sorted_keys[0]
    end = sorted_keys[-1]
    date_list = [end - datetime.timedelta(days=x) for x in range(0, (end-start).days)]
    for date in date_list:
        if date not in bucketed_by_day:
            bucketed_by_day[date] = []

def bucket_by_day(data):
    dates = {}
    for d in data:
        day = datetime.date.fromtimestamp(d['event_timestamp'] / 1000)
        if day in dates:
            dates[day].append(d)
        else:
            dates[day] = [d]
    add_blank_days_to_bucketed_by_day(dates)
    return dates

# returns a bucketed dictionary by the path list, e.g.
# you would bucket by unique users with the following call
#   bucket_by_path(['client', 'client_id'], data)
def bucket_by_path(path_list, data):
    bucketed = {}
    for element in data:
        sub_element = element
        for path in path_list:
            sub_element = sub_element[path]

        if sub_element in bucketed:
            bucketed[sub_element].append(element)
        else:
            bucketed[sub_element] = [element]
    return bucketed

##
## Start of execution
##

data = get_data_from_cache()
events = bucket_events(data)

sum_ = 0
for event in events['DailyGoalComplete']:
	sum_ += event['metrics']['DailyQuestionGoal']

print 'Daily goal average = ' + str(sum_ / len(events['DailyGoalComplete']))

daily_goal_by_day = bucket_by_day(events['DailyGoalComplete'])
daily_goal_by_day_keys = daily_goal_by_day.keys()

##
## Bucket by user, and sort their events
## 

bucketed_by_user = bucket_by_path(['client', 'client_id'], data)
user_first_day = {}
# sort events within user bucket by timestamp
for user in bucketed_by_user.keys():
    bucketed_by_user[user].sort(key=lambda event: event['event_timestamp'])
    first_event = bucketed_by_user[user][0]
    user_first_day[user] = datetime.date.fromtimestamp(first_event['event_timestamp'] / 1000)

# import sys
# print 'exiting'
# sys.exit()

##
## Plot daily goal by day
##

import numpy as np
import matplotlib.pyplot as plt

daily_goal_analysis_details = {}
dg_sorted_keys = sorted(daily_goal_by_day.keys())
dg_sorted_data = []
dg_sorted_data_minus_first_day = []
for idx, key in enumerate(dg_sorted_keys):
    daily_goal_day_events = daily_goal_by_day[dg_sorted_keys[idx]]

    first_day_len = 0
    for daily_goal_event in daily_goal_day_events:
        if key != user_first_day[daily_goal_event['client']['client_id']]:
            first_day_len += 1

    dg_sorted_data.append( len(daily_goal_day_events) )
    dg_sorted_data_minus_first_day.append(first_day_len)

print 'Non-first day total daily goals = ' + str(sum(dg_sorted_data_minus_first_day))

plt.plot(dg_sorted_keys, dg_sorted_data, 'r-', dg_sorted_keys, dg_sorted_data_minus_first_day, 'g-')
plt.legend(['daily goal count', 'daily goal count, but not first day'])
plt.ylabel('Daily Goal Count')
plt.xlabel('Day')
plt.title("Daily Goals Counted by Day")
plt.grid(True)
plt.show()
