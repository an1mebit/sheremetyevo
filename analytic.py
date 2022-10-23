import networkx as nx
import pandas as pd
import json
import datetime
import dateutil
import numpy as np

point_cloud_data = pd.read_excel('src/Distance.xlsx', sheet_name='Roads')
location_data = pd.read_excel('src/Distance.xlsx', sheet_name='Points')
location_data['location_id'] = location_data['location_id'].astype(str)

di_grapth = nx.MultiDiGraph()
for i in range(point_cloud_data.shape[0]):
    row = point_cloud_data.iloc[i]
    di_grapth.add_edge(row['source_point_id'], row['target_point_id'], weight=row['distance'])

def get_matrix_info(start, end):
    path = nx.shortest_path(di_grapth, start, end, 'weight')
    len = nx.shortest_path_length(di_grapth, start, end, 'weight')
    return path, len

def get_time_list(time_end, time):
    now_date = datetime.datetime.now().date()
    time_end = dateutil.parser.parse(time_end)
    time_end = datetime.datetime(now_date.year, now_date.month, now_date.day, time_end.hour, time_end.minute, time_end.second)
    return (time_end - datetime.timedelta(seconds=time)).strftime('%H:%M:%S')

def get_specific_items(relevant_riders, size_people):
    relevant_riders_specific = []
    for rider in relevant_riders:
        if rider['bus_con']['size_people'] == size_people:
            relevant_riders_specific.append(rider)
    return relevant_riders_specific

def get_location_by_path(path):
    for station in path:
        a = location_data.point_id[(location_data['point_id'] == station)].index
        if a.shape[0] != 0:
            path[path.index(station)] = f"{location_data.iloc[a[0]]['location_id']}"
        else:
            path[path.index(station)] = "none"
    return path

def get_task_info(json_from_net):
    relevant_riders = []
    for rider in json_from_net['all_riders']:
        now_date = datetime.datetime.now().date()
        current_time = dateutil.parser.parse(json_from_net['current_time'])
        current_time = datetime.datetime(now_date.year, now_date.month, now_date.day, current_time.hour, current_time.minute, current_time.second)

        time_create_action = dateutil.parser.parse(json_from_net['task']['time_create_action'])
        time_create_action = datetime.datetime(now_date.year, now_date.month, now_date.day, time_create_action.hour, time_create_action.minute, time_create_action.second)
        
        task_point_index = location_data.point_id[(location_data['point_id'] == json_from_net['task']['gate_type'])].index
        task_point_index = location_data.location_id[(location_data['location_id'] == json_from_net['task']['gate_type'])].index
        task_point = location_data.iloc[task_point_index[0]]['point_id']

        if json_from_net['task']['fly_type_landing'] == "departure":
            path, len = get_matrix_info(task_point, rider['busraider_connect'][0]['p_end_connect'])
            time = int((15 + 30 + len / (1000 / 60))*60)
        if json_from_net['task']['fly_type_landing'] == "arrival":
            path, len = get_matrix_info(task_point, rider['busraider_connect'][0]['p_end_connect'])
            time = int((15 + len / (1000 / 60) )*60)
        if current_time + datetime.timedelta(seconds=time) <= time_create_action:
            is_relevant = False
            if np.asarray(rider['busraider_connect']).shape[0] == 0:
                is_relevant = True
            for task in rider['busraider_connect']:
                time_end = dateutil.parser.parse(task['time_end'])
                time_end = datetime.datetime(now_date.year, now_date.month, now_date.day, time_end.hour, time_end.minute, time_end.second)
                if current_time + datetime.timedelta(seconds=time) > time_end:
                    break
                if current_time + datetime.timedelta(seconds=time) < time_end:
                    is_relevant = True
            if is_relevant == True:
                relevant_riders.append(rider)
                relevant_riders[-1]['time'] = time
                relevant_riders[-1]['path'] = path

    airplane_capacity = json_from_net['task']['size_passenger']
    iter_num = np.asarray(relevant_riders).shape[0]
    ids = 0
    path = []
    result = []
    for i in range(iter_num):
        if airplane_capacity >= 0:
            if airplane_capacity >= 100:
                specific_vehicle = get_specific_items(relevant_riders, 100)
                if np.asarray(specific_vehicle).shape[0] != 0:
                    min_len_item = min(specific_vehicle, key=lambda x:x['time'])
                    airplane_capacity = airplane_capacity - min_len_item['bus_con']['size_people']
                    result.append({
                        'id': min_len_item['busraider_connect'][0]['bus_raider_connect'],
                        'path': min_len_item['path'],
                        'time_start': get_time_list(json_from_net['task']['time_create_action'],min_len_item['time']),
                        'time_end': json_from_net['task']['time_create_action']
                    })
                    relevant_riders.remove(min_len_item)
                else:
                    specific_vehicle = get_specific_items(relevant_riders, 50)
                    min_len_item = min(specific_vehicle, key=lambda x:x['time'])
                    airplane_capacity = airplane_capacity - min_len_item['bus_con']['size_people']
                    result.append({
                        'id': min_len_item['busraider_connect'][0]['bus_raider_connect'],
                        'path': min_len_item['path'],
                        'time_start': get_time_list(json_from_net['task']['time_create_action'],min_len_item['time']),
                        'time_end': json_from_net['task']['time_create_action']
                    })
                    relevant_riders.remove(min_len_item)
            if airplane_capacity <= 50:
                specific_vehicle = get_specific_items(relevant_riders, 50)
                if np.asarray(specific_vehicle).shape[0] != 0:
                    min_len_item = min(specific_vehicle, key=lambda x:x['time'])
                    airplane_capacity = airplane_capacity - min_len_item['bus_con']['size_people']
                    result.append({
                        'id': min_len_item['busraider_connect'][0]['bus_raider_connect'],
                        'path': min_len_item['path'],
                        'time_start': get_time_list(json_from_net['task']['time_create_action'],min_len_item['time']),
                        'time_end': json_from_net['task']['time_create_action']
                    })
                    relevant_riders.remove(min_len_item)
                else:
                    specific_vehicle = get_specific_items(relevant_riders, 100)
                    min_len_item = min(specific_vehicle, key=lambda x:x['time'])
                    airplane_capacity = airplane_capacity - min_len_item['bus_con']['size_people']
                    result.append({
                        'id': min_len_item['busraider_connect'][0]['bus_raider_connect'],
                        'path': min_len_item['path'],
                        'time_start': get_time_list(json_from_net['task']['time_create_action'],min_len_item['time']),
                        'time_end': json_from_net['task']['time_create_action']
                    })
                    relevant_riders.remove(min_len_item)
            if airplane_capacity > 50 and airplane_capacity < 100:
                min_len_item = min(relevant_riders, key=lambda x:x['time'])
                airplane_capacity = airplane_capacity - min_len_item['bus_con']['size_people']
                result.append({
                    'id': min_len_item['busraider_connect'][0]['bus_raider_connect'],
                    'path': min_len_item['path'],
                    'time_start': get_time_list(json_from_net['task']['time_create_action'],min_len_item['time']),
                    'time_end': json_from_net['task']['time_create_action']
                })
                relevant_riders.remove(min_len_item)
        else:
            break

    return result