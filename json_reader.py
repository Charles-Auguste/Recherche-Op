#################################################################
# json_reader.py
# Authors : Charles-Auguste Gourio, Thomas Risola, Michel Senegas
# Date : 01/12/2021
#################################################################

import json


def read_data(file_name):
    """Read the project data from a .json file"""
    with open(file_name) as json_data:
        data_dict = json.load(json_data)
    param_dict = data_dict["parameters"]
    clients_dict = data_dict["clients"]
    sites_dict = data_dict["sites"]
    siteSiteDistances_dict = data_dict["siteSiteDistances"]
    siteClientDistances_dict = data_dict["siteClientDistances"]

    return param_dict,clients_dict,sites_dict, siteSiteDistances_dict, siteClientDistances_dict


def encode_x(x):
    """Modify a solution list x into a solution dictionary"""
    rep = {"productionCenters":[],"distributionCenters":[],"clients":[]}
    for i in range(len(x[0])):
        if x[0][i]:
            rep["productionCenters"].append({"id":i+1,"automation":x[2][i]})
        elif x[1][i]:
            rep["distributionCenters"].append({"id":i+1,"parent":x[3][i]+1})
    for i in range(len(x[4])):
        rep["clients"].append({"id":i+1,"parent":x[4][i]+1})
    return rep


def write_data(data_dictionary,file_name):
    file = open(file_name,'w')
    json.dump(data_dictionary,file)
    file.close()
