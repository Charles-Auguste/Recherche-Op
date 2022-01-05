# Imports
import random
import numpy as np
import json_reader as jr
import matplotlib.pyplot as plt
import PL as pl
import os as os
from datetime import datetime
import cout as co

# Données

file = "KIRO-large"

file_name = file + ".json"
file_name_path = "instances/" + file_name
file_name_sol = "sol-" + file_name
name_dir = "solution/" + file + "___derniere_chance___" + str(datetime.now().date()) + "___" + str(
    datetime.now().hour) + "_" + str(datetime.now().minute) + "_" + str(datetime.now().second)
file_name_sol_path = name_dir + "/" + file_name_sol

parameters, clients, sites, siteSiteDistances, siteClientDistances = jr.read_data(file_name_path)
nb_client = len(clients)
nb_site = len(sites)
# print("nb_clients = ", nb_client)
# print("nb_sites = ", nb_site)

class Super_site:
    id: int
    coordinates: list
    demand: int
    children: list

    def __init__(self, _id, _coord, _demand):
        self.id = _id
        self.coordinates = _coord
        self.demand = _demand
        self.parent = 0
        self.children = []


def norm(coord1, coord2):
    value = (coord1[0] - coord2[0]) * (coord1[0] - coord2[0]) + (coord1[1] - coord2[1]) * (coord1[1] - coord2[1])
    value = np.sqrt(value)
    return value


def re_allocation(liste_client: list, liste_site: list):
    predictions = [0 for i in range(nb_client)]
    numpy_siteClientDistances = np.asarray(siteClientDistances)
    for i in range(nb_client):
        j_min = np.argmin(numpy_siteClientDistances[:, i])
        predictions[i] = j_min

    list_super_site = []
    for site in liste_site:
        list_super_site.append(Super_site(site["id"], site["coordinates"], 0))

    for i in range(len(predictions)):
        if(list_super_site[predictions[i]].demand + liste_client[i]["demand"] < 2500000):
            list_super_site[predictions[i]].children.append(liste_client[i]["id"])
            list_super_site[predictions[i]].demand += liste_client[i]["demand"]
        else:
            '''
            numpy_siteClientDistances = np.asarray(siteClientDistances)
            numpyS = numpySi[:, i]

            k = 2
            idx = np.argpartition(numpyS, k)
            idx_2eme_site_plus_proche = idx[:k][1]
            list_super_site[idx_2eme_site_plus_proche].children.append(liste_client[i]["id"])
            list_super_site[idx_2eme_site_plus_proche].demand += liste_client[i]["demand"]
            
                '''
            numpyS = numpy_siteClientDistances[:, i]
            k = 2
            idx = np.argpartition(numpyS, k)
            idx_2eme_site_plus_proche = idx[:k][1]
            list_super_site[idx_2eme_site_plus_proche].children.append(liste_client[i]["id"])
            list_super_site[idx_2eme_site_plus_proche].demand += liste_client[i]["demand"]
            if (list_super_site[idx_2eme_site_plus_proche].demand + liste_client[i]["demand"] < 2500000):
                list_super_site[idx_2eme_site_plus_proche].children.append(liste_client[i]["id"])
                list_super_site[idx_2eme_site_plus_proche].demand += liste_client[i]["demand"]
            else:
                k = 3
                idx = np.argpartition(numpyS, k)
                idx_3eme_site_plus_proche = idx[:k][2]
                list_super_site[idx_3eme_site_plus_proche].children.append(liste_client[i]["id"])
                list_super_site[idx_3eme_site_plus_proche].demand += liste_client[i]["demand"]
    return list_super_site


def link_shortest_client(liste_client: list, liste_site: list, parameters, siteClDist):
    set_client = liste_client.copy()
    list_super_site = []
    for site in liste_site:
        list_super_site.append(Super_site(site["id"], site["coordinates"], 0))
    while len(set_client) != 0:
        for i in range(len(liste_site)):
            if(len(set_client) != 0):
                min_dist = norm(liste_site[i]["coordinates"],set_client[0]["coordinates"])
                id_min_dist = set_client[0]["id"]
                for j in range(len(set_client)):
                    new_dist = norm(liste_site[i]["coordinates"],set_client[j]["coordinates"])
                    if new_dist < min_dist:
                        min_dist = new_dist
                        id_min_dist = set_client[j]["id"]
                list_super_site[i].children.append(id_min_dist)
                indice_a_suppr = 0
                for k in range(len(set_client)):
                    if set_client[k]["id"] == id_min_dist:
                        indice_a_suppr = k
                del set_client[indice_a_suppr]
    """
    for super_site in list_super_site:
        print("=======")
        print(super_site.id)
        print(super_site.coordinates)
        print(super_site.children)
        print("=======")
    """
    return list_super_site

def check_region(site_var_f, nb_clien):
    count = 0
    for site in site_var_f:
        for el in site.children:
            count += 1
    print(count == nb_clien)

def show_client_site(name,site_var):
    X = [[] for i in range(len(site_var))]
    Y = [[] for i in range(len(site_var))]
    x2=[]
    y2=[]
    for i in range(len(site_var)):
        for id_client in site_var[i].children:
            X[i].append(clients[id_client-1]["coordinates"][0])
            Y[i].append(clients[id_client-1]["coordinates"][1])
    for i in range(len(site_var)):
        plt.scatter(X[i], Y[i])
    for id_site in range(nb_site):
        x2.append(sites[id_site]["coordinates"][0])
        y2.append(sites[id_site]["coordinates"][1])

    plt.scatter(x2, y2,marker='x')

    plt.title('Répartition des clients et des sites')
    plt.xlabel('x')
    plt.ylabel('y')

    #plt.savefig(name + '/Repartition_normale.png')
    plt.show()

def build_solution_simple(site_var_f,nb_sit, nb_clien, list_clien, list_sit):
    X_prod = [1 for i in range(nb_sit)]
    X_distr = [0 for i in range(nb_sit)]
    X_auto =  [1 for i in range(nb_sit)]
    X_parent = [[0 for i in range(nb_sit)] for i in range(nb_sit)]
    X_client = [[0 for i in range(nb_sit)] for i in range(nb_clien)]
    a=1
    for site in site_var_f:
        print("demand site ", a, " : ", site.demand)
        a+=1
    for site in site_var_f:
        for id_child in site.children:
            X_client[id_child - 1][site.id - 1] = 1

    site_demand_trie = sorted(site_var_f, key=lambda site: site.demand)
    for i in range(15):
        X_prod[site_demand_trie[i].id - 1] = 1
        X_distr[site_demand_trie[i].id - 1] = 0
        X_auto[site_demand_trie[i].id - 1] = 0
    numpy_siteSiteDistance = np.asarray(siteSiteDistances)
    numpyS = numpy_siteSiteDistance[:, 13]
    k = 2
    idx = np.argpartition(numpyS, k)
    idx_2eme_site_plus_proche = idx[:k][1]
    X_parent[13][idx_2eme_site_plus_proche] = 0
    return ([X_prod,X_distr,X_auto,X_parent,X_client])


if __name__ == "__main__":
    """
    os.makedirs(name_dir, exist_ok=True)
    set_super_client = glouton_super_client(2, 0, clients, parameters, True)
    link_distribution(set_super_client, sites, 1)
    show_client_site(name_dir)
    show_super_client(set_super_client, sites, name_dir)
    # X = create_solution(parameters,clients,sites,set_super_client)
    X = pl.solution_pl(parameters,clients,sites,siteSiteDistances,siteClientDistances, set_super_client)
    pl.check_constraint(X,len(sites), len(clients))
    jr.write_data(jr.encode_x(X),file_name_sol_path)
    print(co.total_cost(X,parameters,clients,sites,siteSiteDistances,siteClientDistances)/10000)
    print(X)
    """
    #site_var = link_shortest_client(clients,sites,parameters, siteClientDistances)
    site_var = re_allocation(clients,sites)
    show_client_site("blabla3.png",site_var)
    check_region(site_var,len(clients))
    X = build_solution_simple(site_var,len(sites), len(clients), clients, sites)
    pl.check_constraint(X,len(sites), len(clients))
    print(co.total_cost(X, parameters, clients, sites, siteSiteDistances, siteClientDistances) / 10000)
    os.makedirs(name_dir, exist_ok=True)
    jr.write_data(jr.encode_x(X), file_name_sol_path)