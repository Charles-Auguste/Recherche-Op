import json

def read_data(file_name):
    with open(file_name) as json_data:
        data_dict = json.load(json_data)
    param_dict = data_dict["parameters"]
    clients_dict = data_dict["clients"]
    sites_dict = data_dict["sites"]
    siteSiteDistances_dict = data_dict["siteSiteDistances"]
    siteClientDistances_dict = data_dict["siteClientDistances"]

    return param_dict,clients_dict,sites_dict, siteSiteDistances_dict, siteClientDistances_dict



