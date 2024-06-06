"""
@author: akalenkova (anna.kalenkova@adelaide.edu.au)
"""

from pm4py.objects.log.obj import Event
import  datetime


def extract_knockouts_and_times(log):
    knockout_dictionary = {}
    times_dictionary = {}
    for trace in log:
        for event in trace:
            name = event['concept:name']
            if not name in knockout_dictionary.keys():
                    knockout_dictionary[name] = 1
            else:
                    knockout_dictionary[name] += 1
    for trace in log:
        first = True
        for next_event in trace:
            if not first:
                time = next_event['time:timestamp'] - event['time:timestamp']
            else:
                time = datetime.datetime(1,1,1,0,0) - datetime.datetime(1,1,1,0,0)
            name = next_event['concept:name']
            knockout = event['concept:name']
            if (name == "Declaration APPROVED by ADMINISTRATION") or (name == "Declaration REJECTED by ADMINISTRATION"):
                name = "Declaration APPROVED-REJECTED by ADMINISTRATION"
            if (name == "Declaration APPROVED by BUDGET OWNER") or (name == "Declaration REJECTED by BUDGET OWNER"):
                 name = "Declaration APPROVED-REJECTED by BUDGET OWNER"
            if (name == "Declaration APPROVED by PRE_APPROVER") or (name == "Declaration REJECTED by PRE_APPROVER"):
                 name = "Declaration APPROVED-REJECTED by PRE_APPROVER"
            if (name == "Declaration FINAL_APPROVED by SUPERVISOR") or (name == "Declaration REJECTED by SUPERVISOR"):
                name = "Declaration APPROVED-REJECTED by SUPERVISOR"
            if not name in times_dictionary.keys():
                times_dictionary[name] = [time.total_seconds()//3600]
            else:
                times_dictionary[name].append(time.total_seconds()//3600)

            event = next_event
            first = False
    knockout_dictionary_clean = {}
    for name in set(times_dictionary.keys()):
        if name == "Declaration APPROVED-REJECTED by ADMINISTRATION":
            knockout_dictionary_clean[name] = knockout_dictionary["Declaration REJECTED by ADMINISTRATION"]/(knockout_dictionary["Declaration APPROVED by ADMINISTRATION"]+knockout_dictionary["Declaration REJECTED by ADMINISTRATION"])
        elif name == "Declaration APPROVED-REJECTED by BUDGET OWNER":
            knockout_dictionary_clean[name] =  knockout_dictionary["Declaration REJECTED by BUDGET OWNER"]/(knockout_dictionary["Declaration APPROVED by BUDGET OWNER"]+knockout_dictionary["Declaration REJECTED by BUDGET OWNER"])
        elif name == "Declaration APPROVED-REJECTED by PRE_APPROVER":
            knockout_dictionary_clean[name] =  knockout_dictionary["Declaration REJECTED by PRE_APPROVER"]/(knockout_dictionary["Declaration APPROVED by PRE_APPROVER"]+knockout_dictionary["Declaration REJECTED by PRE_APPROVER"])
        elif name == "Declaration APPROVED-REJECTED by SUPERVISOR":
            knockout_dictionary_clean[name] =  knockout_dictionary["Declaration REJECTED by SUPERVISOR"]/(knockout_dictionary["Declaration REJECTED by SUPERVISOR"]+knockout_dictionary["Declaration FINAL_APPROVED by SUPERVISOR"])


    return knockout_dictionary_clean, times_dictionary

def convert_name_to_new_name(name):
    if (name == "Declaration APPROVED by ADMINISTRATION") or (name == "Declaration REJECTED by ADMINISTRATION"):
        new_name = "Declaration APPROVED-REJECTED by ADMINISTRATION"
    elif (name == "Declaration APPROVED by BUDGET OWNER") or (name == "Declaration REJECTED by BUDGET OWNER"):
        new_name = "Declaration APPROVED-REJECTED by BUDGET OWNER"
    elif (name == "Declaration APPROVED by PRE_APPROVER") or (name == "Declaration REJECTED by PRE_APPROVER"):
        new_name = "Declaration APPROVED-REJECTED by PRE_APPROVER"
    elif (name == "Declaration FINAL_APPROVED by SUPERVISOR") or (name == "Declaration REJECTED by SUPERVISOR"):
        new_name = "Declaration APPROVED-REJECTED by SUPERVISOR"
    else:
        new_name = name
    return new_name

def update_precedence_constraints(precedence_constraints):
    new_precedence_constraints = {}
    for name in precedence_constraints.keys():
        new_name = convert_name_to_new_name(name)
        new_precedence_constraints[new_name] =set()
        for prec in precedence_constraints[name]:
            new_precedence_constraints[new_name].add(convert_name_to_new_name(prec))
    return new_precedence_constraints
