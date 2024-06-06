from pm4py.objects.log.importer.xes import importer as xes_importer
import sys, json, copy, random, time
import log_parser
import numpy as np


def find_activities_with_same_constraints(activity, added_activities):
    same_activities = set()
    for a in added_activities:
        if precedence_constraints[a] == precedence_constraints[activity]:
            same_activities.add(a)
    return same_activities

def find_leaves(activities):
    leaves = set()
    for a1 in activities:
        isLeaf = True
        for a2 in activities:
            if a1 in final_connections[a2]:
                isLeaf = False
        if isLeaf:
            leaves.add(a1)
    return leaves

def sum_of_two_times(time1, prob, time2):
    sum_time = []
    for t1 in time1:
        for t2 in time2:
            sum_time.append(t1+prob*t2)
    return sum_time

def max_time_between_two(time1, time2):
    max_time = []
    for t1 in time1:
        for t2 in time2:
            if t1 > t2:
                max_time.append(t1)
            else:
                max_time.append(t2)
    return max_time

def calc_total_time(activity_times, all_activities):
    total_time = activity_times
    for a in all_activities:
        total_time = max_time_between_two(completion_times[a], total_time)

    return total_time

def calculate_execution_probability(activity):
    p = 1 - knockouts[activity]
    while activity in final_connections.keys():
        prev_activity = list(final_connections[activity])[0]
        if prev_activity == "":
            break
        p = p * (1 - knockouts[prev_activity])
        activity = prev_activity

    return p

def find_connected(activity):
    connected = {activity}
    while activity in final_connections.keys():
        prev_activity = list(final_connections[activity])[0]
        if prev_activity == "":
            break
        connected.add(prev_activity)
        activity = prev_activity

    return connected                    


variant = xes_importer.Variants.ITERPARSE
parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
log = xes_importer.apply('logs/' + sys.argv[1], variant=variant, parameters=parameters)


# READ PRECEDENCE CONSTRAINS
f = open('logs/' + sys.argv[2])
precedence_constraints = json.load(f)
precedence_constraints = log_parser.update_precedence_constraints(precedence_constraints)
#print(precedence_constraints)

# EXTRACT KNOCKOUT PROBABILITIES AND TIMES FROM THE EVENT LOG
times = {}
knockouts = {}
knockouts, times = log_parser.extract_knockouts_and_times(log)


# FIND THE PROPRITIES OF ACTIVITIES
priorities = {}
for act in times.keys():
    if act not in knockouts.keys():
        knockouts[act] = 0
    act_times = times[act]
    if act in knockouts.keys():
        act_knockout = knockouts[act]
    else:
        act_knockout = 0
    if act_knockout != 0:
        priorities[act] = np.average(act_times)/act_knockout
    else:
        priorities[act] = np.iinfo(np.int16).max
all_new_activities = set(times.keys())
added_activities = set()
completion_times = {}
final_connections = {}

# PICK A NEW ACTIVITY AND CONNECT IT
while len(all_new_activities) > 0:
    priority = np.iinfo(np.int16).max +1 
    for a in all_new_activities:
        if priorities[a] < priority:
               new_activity = a
               priority = priorities[a]
    #print(new_activity)
    print()
    print("Adding activity:")
    print(new_activity)
    # FIND ACTIVITIES WITH THE SAME PRECEDENCE CONSTRAINTS
    activities_with_same_constraints = find_activities_with_same_constraints(new_activity, added_activities)
    leaves = find_leaves(activities_with_same_constraints)
    # FIND THE BEST CONNECTION FOR THE NEW ACTIVITY
    temp_leaves = copy.deepcopy(leaves)
    temp_times = calc_total_time(times[new_activity], temp_leaves)
    avg_total_time = np.average(temp_times)
    print("Initial time:")
    print(avg_total_time)
    time.sleep(1)

    connected_activity= ""
    best_times = temp_times
    print("Leaves:")
    print(leaves)
    for same_activity in activities_with_same_constraints:
        print("Checking activity:")
        print(same_activity)
        p = calculate_execution_probability(same_activity)
        print("Knockut probability:")
        print(1-p)
        sum_time = sum_of_two_times(completion_times[same_activity], p, times[new_activity])
        temp_leaves = copy.deepcopy(leaves)
        if same_activity in temp_leaves: 
            temp_leaves.remove(same_activity)
        temp_times = calc_total_time(sum_time, temp_leaves)
        avg_temp_total_time = np.average(temp_times)
        print("Time:")
        print(avg_temp_total_time)
        time.sleep(1)
        if int(avg_temp_total_time) < int(avg_total_time):
            connected_activity = same_activity
            best_times = temp_times
            avg_total_time = np.average(best_times)
    final_connections[new_activity] = set()
    final_connections[new_activity].add(connected_activity)
    print("Connecting activity to " + str(connected_activity))
    if connected_activity == "":
        completion_time = times[new_activity]
    else:
        p = calculate_execution_probability(connected_activity)
        completion_time = sum_of_two_times(completion_times[connected_activity], p, times[new_activity])
    completion_times[new_activity] = np.random.choice(completion_time, 50)
    print(completion_times[new_activity])

    all_new_activities.remove(new_activity)
    added_activities.add(new_activity)

print(final_connections)




    

    






