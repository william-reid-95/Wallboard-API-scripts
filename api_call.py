from pprint import pprint
import json
import datetime
import time
import requests
import asyncio
import aiohttp


#Creates Session for agents response
s_agent = requests.Session()
#Creates Session for queue response
s_queue = requests.Session()

def convert_seconds_to_time(n):
    """converts seconds int to HH:MM:SS"""
    if n is not None:
        return str(datetime.timedelta(seconds = n))
    else:
        return ""

def get_sec(time_str):
    """Get seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

def convert_last_midnight_to_utc_ms():
    now_ms = int(time.time()*1000)
    t = time.localtime()
    ms_since_midnight = (t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec) * 1000
    output = now_ms - ms_since_midnight
    return output

def get_agent_task(session, email_list):
    tasks = []

    url = "https://dnaypqq185.execute-api.eu-central-1.amazonaws.com/prod/asd-universal-interface-get-agent-call-statictics"

    headers = {
    'App-Key': 'fkorgewk985w8g54jgd832jv9igr-grew3grewg5r7_grefr4254t32',
    'Content-Type': 'application/json'
    }
    for emails in email_list:
        payload = json.dumps({
        "instance_name": "dxc-ito-mws-asia-ml",
        "start_time": convert_last_midnight_to_utc_ms(), #1659045600000
        "name_list": emails
        })
        tasks.append(session.request("GET", url, headers=headers, data=payload))
    return tasks

async def get_agent_data(email_list):
    json_data = []
    start = time.time()
    async with aiohttp.ClientSession() as session:
        
        tasks = get_agent_task(session, email_list)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            json_return = await response.json()
            json_data.append(json_return)    
    print(f"Agent response: {time.time() - start}")
    print(f"Agent status: {response.reason}")
    return json_data


def clean_agent_data(json_data) -> list:
    output_dict_list = []
    try:
        for item in json_data:
            for agent_stats in item['data']:
                if agent_stats['stats']['agent_activity'] != 'Offline' and agent_stats['stats']['agent_activity'] != '':
                    agent_data = {
                        'Agent': agent_stats['user_name'],
                        'Activity': agent_stats['stats']['agent_activity'],
                        'Duration': convert_seconds_to_time(agent_stats['stats']['agent_activity_duration']),
                        'Agent Name' : agent_stats['stats']['agent_name'],
                        'Handled in' : str(agent_stats['stats']['handled_in']),
                        'Handled out' : str(agent_stats['stats']['handled_out']),
                        'AHT' : convert_seconds_to_time(agent_stats['stats']['average_handle_time'])
                        }
                    output_dict_list.append(agent_data)
    except:
        pass
    return output_dict_list


def get_queue_tasks(session,queue_query_list):
    tasks = []

    url = "https://dnaypqq185.execute-api.eu-central-1.amazonaws.com/prod/asd-universal-interface-get-queue-call-statictics"

    headers = {
    'App-Key': 'fkorgewk985w8g54jgd832jv9igr-grew3grewg5r7_grefr4254t32',
    'Content-Type': 'application/json'
    }
    for queues in queue_query_list:
        payload = json.dumps({
        "instance_name": "dxc-ito-mws-asia-ml",
        "instance_id": "d6398590-db2f-4fe0-ac02-9530f9360f43",
        "start_time": convert_last_midnight_to_utc_ms(),
        "name_list":  queues
        })
        tasks.append(session.request("GET", url, headers=headers, data=payload))
    return tasks

async def get_queue_data(queue_query_list):
    json_data = []
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = get_queue_tasks(session,queue_query_list)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            json_return = await response.json()
            json_data.append(json_return)
    print(f"Queue response: {time.time() - start}")
    print(f"Queue status: {response.reason}")
    return json_data

def clean_queue_data(json_data) -> list:
    output_dict_list = [calculate_queue_totals(json_data)]
    try:
        for item in json_data:
            for queue_stats in item['data']:
                #KEYS: "Name","Online","NPT","In queue","Oldest","Queued","Handled","Abandoned","AHT","SL 60 secs"
                queue_data = {
                    'Name': queue_stats['queue_name'],
                    'Online': queue_stats['stats']['agents_online'],
                    'In queue': queue_stats['stats']['in_queue'], 
                    'Oldest': queue_stats['stats']['oldest'], 
                    'Queued': (queue_stats['stats']['queued'] - queue_stats['stats']['handled']), 
                    'Handled': queue_stats['stats']['handled'], 
                    'Abandoned': queue_stats['stats']['abandoned'], 
                    'AHT': queue_stats['stats']['oldest'], 
                    'SL 60 secs': int((queue_stats['stats']['sl_60'])*100), 
                    }
                output_dict_list.append(queue_data)
        return output_dict_list
    except:
        pass

def calculate_queue_totals(json_data):
    for item in json_data:
        count = len(item['data'])
        total_agents = 0
        total_in_queue = 0
        total_calls = 0
        total_passed = 0
        try:
            for queue_stats in item['data']:
                total_agents += queue_stats['stats']['agents_online']
                total_in_queue += queue_stats['stats']['in_queue']
                total_calls += queue_stats['stats']['handled']
                total_passed += (queue_stats['stats']['handled']*queue_stats['stats']['sl_60'])
                # show sla stats
                # print(f"total: {queue_stats['stats']['handled']}, passed: {(queue_stats['stats']['handled']*queue_stats['stats']['sl_60'])}, SLA: {queue_stats['stats']['sl_60']}")
            
            overall_sla = int((total_passed/total_calls)*100)

            overall_queue_data = {
                        'Name': 'Summary',
                        'Online': total_agents,
                        'In queue': total_in_queue, 
                        'Oldest': 0, 
                        'Queued': 0, 
                        'Handled': total_calls, 
                        'Abandoned': 0, 
                        'AHT': 0, 
                        'SL 60 secs': overall_sla, 
                        }
            return overall_queue_data
        except:
            return None
