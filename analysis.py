import json
import aws_mobile_analytics_data_parser as aws_madp

def get_data_from_cache():
    with open('data.json') as data_file:    
        data = json.load(data_file)
	return data

data = get_data_from_cache()
aws_madp.jprint(data[0])

events = {}
for d in data:
    if d['event_type'] not in events:
        events[d['event_type']] = []
    events[d['event_type']].append(d)

print events['DailyGoalComplete'][0]
sum_ = 0
for event in events['DailyGoalComplete']:
	sum_ += event['metrics']['DailyQuestionGoal']

print 'Daily goal average = ' + str(sum_ / len(events['DailyGoalComplete']))

