import numpy as np
import json_reader as jr

def genere_sol_admissible(clients,sites):
    nb_client = len(clients)
    nb_site = len(sites)
    x = [[0 for i in range(nb_site)], [0 for i in range(nb_site)], [0 for i in range(nb_site)],
         [0 for i in range(nb_site)], [0 for i in range(nb_client)]]
    for i in range(len(x[0])):
        r=np.random.randint(-1,2)
        if r>=0:
            x[r][i]=1
            if r==0:
                q=np.random.randint(0,2)
                if q:
                    x[2][i]=1
    for i in range(len(x[0])):
        r = np.random.randint(0,len(x[0]))
        while not x[0][r]:
            r = np.random.randint(0,len(x[0]))
        x[3][i]=r
    for i in range(len(x[4])):
        r = np.random.randint(0,len(x[0]))
        while (not x[0][r]) and (not x[1][r]):
            r = np.random.randint(0,len(x[0]))
        x[4][i]=r
    return x

parameters, clients, sites, siteSiteDistances, siteClientDistances = jr.read_data(file_name)
nb_client = len(clients)
nb_site = len(sites)

def building_cost(s, x):
    """s est le numero du site """
    if (x[0][s - 1] == 1):
        return parameters["buildingCosts"]["productionCenter"] + x[2][s - 1] * parameters["buildingCosts"][
            "automationPenalty"]
    elif (x[1][s - 1] == 1):
        return parameters["buildingCosts"]["distributionCenter"]
    else:
        return 0


def production_cost(i, x):
    """i est le numero du client """
    # if parent = producter
    if (x[0][x[4][i - 1]] == 1):
        # i+1 car les id start a 0 et nos listes a 0
        # x[2][x[4][i-1]] producter automatise?
        auto = x[2][x[4][i - 1]]
        cost = clients[i - 1]["demand"] * (
                    parameters["productionCosts"]["productionCenter"] - auto * parameters["productionCosts"][
                "automationBonus"])
        return cost
    # if parent = distrib
    elif (x[1][x[4][i - 1]] == 1):
        # x[2][x[3][x[4][i-1]]] parent du distrib automatise?
        auto = x[2][x[3][x[4][i - 1]]]
        cost = clients[i - 1]["demand"] * (
                    parameters["productionCosts"]["productionCenter"] - auto * parameters["productionCosts"][
                "automationBonus"] + parameters["productionCosts"]["distributionCenter"])
        return cost
    else:
        return float('inf')


def routing_cost(i, x):
    '''DANGER: On suppose que les clients sont ordonnés dans l'ordre des indices dans clients
    i: numéro du client
    x: solution au format liste de liste décrit plus haut'''
    if x[0][x[4][i - 1]]:
        return clients[i - 1]["demand"] * parameters["routingCosts"]["secondary"] * (
        siteClientDistances[x[4][i - 1]][i - 1])
    elif x[1][x[4][i - 1]]:
        return clients[i - 1]["demand"] * \
               (parameters["routingCosts"]["primary"] * siteClientDistances[x[4][i - 1]][x[3][x[4][i - 1]]] +
                parameters["routingCosts"]["secondary"] * siteClientDistances[x[4][i - 1]][i - 1])
    else:
        return float('inf')


def capacity_cost(s, x):
    if (x[0][s - 1] == 1):
        value = 0
        for i in range(nb_client):
            if (x[4][i - 1] == s or x[3][x[4][i - 1]] == s):
                value += clients[i - 1]["demand"]
        value -= (parameters["capacities"]["productionCenter"] + x[2][s - 1] * parameters["capacities"][
            "automationBonus"])
        value_max = max(0, value * parameters["capacityCost"])
        return value_max
    else:
        return 0


def total_cost(x):
    cost = 0
    for site in sites:
        s = site["id"]
        cost += building_cost(s, x) + capacity_cost(s, x)
    for client in clients:
        i = client["id"]
        cost += production_cost(i, x) + routing_cost(i, x)
    return cost


def heuristique1():
    x = [[0 for i in range(nb_site)],[0 for i in range(nb_site)], [0 for i in range(nb_site)], [0 for i in range(nb_site)], [0 for i in range(nb_client)]]
    total_demand = 0
    for client in clients:
        demand = client["demand"]
        total_demand += demand
    min = 100000000000000000
    number_of_usine = total_demand / parameters["capacities"]["productionCenter"]
    j_used = []
    for i in range(number_of_usine):
        for j in range(nb_site):
            # if la distance moyenne d'un site est plus petite que la moyenne on prend ce site
            dist_moy = np.abs(np.mean(siteClientDistances[:, j]))
            if (dist_moy < min):
                min = dist_moy
                if(j not in j_used):
                    j_choice_to_construct = j
                    j_used.append(j)
    for j in j_used:
        x[0][j] = 1
    dist_usines_ouvertes = {}
    for i in range(nb_client):
        for j in j_used:
            dist_usines_ouvertes[str(j)] = siteClientDistances[i][j]
        usine_plus_proche = int(max(dist_usines_ouvertes, key=dist_usines_ouvertes.get))



    return 0
