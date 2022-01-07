# Imports
import random
import numpy as np
import json_reader as jr
import matplotlib.pyplot as plt
import PL_client as pl_c
import PL as pl
import os as os
from datetime import datetime
import cout as co
import time
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

def show_solution(name,X):
    for id_client in range(nb_client):
        for id_site_pere in range(nb_site):
            if X[4][id_client][id_site_pere] == 1:
                x=[clients[id_client]["coordinates"][0],sites[id_site_pere]["coordinates"][0]]
                y = [clients[id_client]["coordinates"][1], sites[id_site_pere]["coordinates"][1]]
                plt.plot(x,y, color="grey", linewidth=0.5)

    for id_site_fils in range(nb_site):
        for id_site_pere in range(nb_site):
            if X[3][id_site_fils][id_site_pere] == 1:
                x=[sites[id_site_fils]["coordinates"][0],sites[id_site_pere]["coordinates"][0]]
                y = [sites[id_site_fils]["coordinates"][1], sites[id_site_pere]["coordinates"][1]]
                plt.plot(x,y, color="black")

    for id_client in range(nb_client):
        plt.plot(clients[id_client]["coordinates"][0],clients[id_client]["coordinates"][1], color="grey", marker="o", markersize=3)

    for id_site in range(nb_site):
        if X[0][id_site] == 1:
            if X[2][id_site] == 1:
                plt.plot(sites[id_site]["coordinates"][0],sites[id_site]["coordinates"][1], color='red', marker ="o",markersize=12)
            else:
                plt.plot(sites[id_site]["coordinates"][0], sites[id_site]["coordinates"][1], color='orange', marker="o",markersize=12)
        elif X[1][id_site] == 1:
            plt.plot(sites[id_site]["coordinates"][0],sites[id_site]["coordinates"][1], color='green', marker ="o",markersize=12)
        else:
            plt.plot(sites[id_site]["coordinates"][0], sites[id_site]["coordinates"][1], color='grey', marker="o",markersize=12)


    plt.title('Solution trouvée')
    plt.xlabel('x')
    plt.ylabel('y')

    plt.savefig(name + '/solution.png')
    plt.show()

# associe le client au site le plus proche si en dessous du seuil de demande
# sinon on prend le 2eme site le plus proche si cest en dessous du seuil de demande
# seuil demande  = 2 500 000
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


def calcul_demand(X,list_sites, list_clients):
    nombre_site = len(list_sites)
    nombre_clients = len(list_clients)
    demand = [0 for i in range (nombre_site)]
    for i in range(nombre_site):
        for j in range(nombre_clients):
            if (X[4][j][i] == 1): # si le site i sert le client j
                demand[i] += list_clients[j]["demand"]
    return demand

def ameliore_solution(X, list_sites, list_clients, list_siteSite):
    nombre_site = len(list_sites)
    nombre_clients = len(list_clients)
    demand = calcul_demand(X,list_sites,list_clients)
    for i in range(nombre_site):
        if(X[0][i] == 1 and X[2][i] == 0): #centre de production non automatisé
            X[0][i] = 0
            X[1][i] = 1
            X[2][i] = 0
    for i in range(nombre_site):
        if (X[1][i] == 1): # si on est avec un centre de distribution
            for k in range (nombre_site):
                if (X[0][k] == 1 and (demand[k] + demand[i] <= 2500000) and (list_siteSite[i][k] < 186)):
                    if (np.sum(X[3][i]) == 0):
                        X[3][i][k] = 1
    for i in range(nombre_site):
        if (X[0][i] == 0 and (np.sum(X[3][i]) == 0)):
            X[0][i] = 1
            X[1][i] = 0

def build_solution_simple(site_var_f,nb_sit, nb_clien, list_clien, list_sit):
    X_prod = [1 for i in range(nb_sit)]
    X_distr = [0 for i in range(nb_sit)]
    X_auto =  [1 for i in range(nb_sit)]
    X_parent = [[0 for i in range(nb_sit)] for i in range(nb_sit)]
    X_client = [[0 for i in range(nb_sit)] for i in range(nb_clien)]
    a=1
    for site in site_var_f:
        for id_child in site.children:
            X_client[id_child - 1][site.id - 1] = 1

    site_demand_trie = sorted(site_var_f, key=lambda site: site.demand)
    # 15 pour large
    # 20 pour petit
    seuil_site_pas_auto = 16
    for i in range(seuil_site_pas_auto):
        X_prod[site_demand_trie[i].id - 1] = 1
        X_distr[site_demand_trie[i].id - 1] = 0
        X_auto[site_demand_trie[i].id - 1] = 0
        children = site_demand_trie[i].children

        for id_child in children:
            numpy_siteClientDistance = np.asarray(siteClientDistances)
            numpyS = numpy_siteClientDistance[:, id_child - 1]
            k = 3
            idx = np.argpartition(numpyS, k)
            idx = idx[:k]
            idx_2eme_site_plus_proche = idx[2]
            rayon = 29
            if(np.abs(numpyS[idx[0]] - numpyS[idx[1]]) < rayon and X_auto[idx[1]]==1):
                for k in range(nb_site):
                    X_client[id_child - 1][k] = 0
                X_client[id_child - 1][idx[1]] = 1

    return ([X_prod,X_distr,X_auto,X_parent,X_client])

if __name__ == "__main__":
    start = time.time()
    site_var = re_allocation(clients,sites)
    X = build_solution_simple(site_var,len(sites), len(clients), clients, sites)
    end = time.time()
    print("The programm run in ", end - start, " seconds")
    pl.check_constraint(X,len(sites), len(clients))
    os.makedirs(name_dir, exist_ok=True)
    ameliore_solution(X,sites,clients,siteSiteDistances)
    show_solution(name_dir, X)
    #X_client = pl_c.solution_pl(parameters,clients,sites,siteSiteDistances,siteClientDistances,X)
    #X[4] = X_client
    jr.write_data(jr.encode_x(X), file_name_sol_path)
