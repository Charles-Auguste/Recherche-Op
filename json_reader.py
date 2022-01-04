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

    return param_dict, clients_dict, sites_dict, siteSiteDistances_dict, siteClientDistances_dict


def encode_x(x):
    """Modify a solution list x into a solution dictionary"""
    rep = {"productionCenters": [], "distributionCenters": [], "clients": []}
    for i in range(len(x[0])):
        if x[0][i]:
            rep["productionCenters"].append({"id": i + 1, "automation": int(x[2][i])})
        elif x[1][i]:
            rep["distributionCenters"].append({"id": i + 1, "parent": 0})
            count = 1
            for j in range(len(x[0])):
                if x[3][i][j]:
                    rep["distributionCenters"][-1]["parent"] = count
                count += 1
    for i in range(len(x[4])):
        rep["clients"].append({"id": i + 1, "parent": 0})
        count = 1
        for j in range(len(x[0])):
            if x[4][i][j]:
                rep["clients"][-1]["parent"] = count
            count += 1
    return rep


def write_data(data_dictionary, file_name):
    file = open(file_name, 'w')
    json.dump(data_dictionary, file)
    file.close()


# pour réutiliser une solution precedente
def decode(filename):
    file = open(filename, 'r', encoding="utf-8")
    dict_list = json.load(file)
    x = []
    n_site = max(dict_list["productionCenters"][-1]["id"], dict_list["distributionCenters"][-1]["id"]) - 1
    n_client = dict_list["clients"][-1]["id"]
    x_site = [0 for i in range(n_site)]
    x_dist = [0 for i in range(n_site)]
    x_auto = [0 for i in range(n_site)]
    x_pare = [[0 for i in range(n_site)] for i in range(n_site) ]
    x_clie = [[0 for i in range(n_site)] for i in range(n_client)]

    for i in range(len(dict_list["productionCenters"])):
        x_site[dict_list["productionCenters"][i]["id"] - 1] = 1
        x_auto[dict_list["productionCenters"][i]["id"] - 1] = dict_list["productionCenters"][i]["automation"]

    for i in range(len(dict_list["distributionCenters"])):
        x_dist[dict_list["distributionCenters"][i]["id"] - 1] = 1
        x_pare[dict_list["distributionCenters"][i]["id"] - 1][dict_list["distributionCenters"][i]["parent"] - 1] = 1

    for i in range(len(dict_list["clients"])):
        x_clie[dict_list["clients"][i]["id"] - 1][dict_list["clients"][i]["parent"] - 1] = 1

    x.append(x_site)
    x.append(x_dist)
    x.append(x_auto)
    x.append(x_pare)
    x.append(x_clie)
    file.close()
    return x
