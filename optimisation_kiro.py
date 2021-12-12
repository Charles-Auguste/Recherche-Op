import random
import numpy as np
import json_reader as jr
import pulp
import json


def genere_sol_admissible(clients,sites):
    nb_client = len(clients)
    nb_site = len(sites)
    x = [[0 for i in range(nb_site)], [0 for i in range(nb_site)], [0 for i in range(nb_site)],
         [0 for i in range(nb_site)], [0 for i in range(nb_client)]]
    listeusine=[]
    listesiteson=[]
    for i in range(len(x[0])):
        r=np.random.randint(-1,2)
        if r>=0:
            x[r][i]=1
            listesiteson.append(i)
            if r==0:
                listeusine.append(i)
                q=np.random.randint(0,2)
                if q:
                    x[2][i]=1
    if not len(listeusine):
        r=np.random.randint(len(x[0]))
        listeusine.append(r)
        listesiteson.append(r)
        x[1][r]=0
        x[0][r]=1
    for i in range(len(x[0])):
        r = np.random.choice(listeusine)
        x[3][i]=r
    for i in range(len(x[4])):
        r = np.random.choice(listesiteson)
        x[4][i]=r
    return x

file_name = "KIRO-large.json"
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

def check_constraint(x,nb_site, nb_client):
    for i in range(nb_site):
        # tout est positif
        if (x[0][i] < 0 or x[1][i] < 0 or x[2][i] < 0 or x[3][i] < 0):
            return 1
        # 1 site est occupé par une seule usine
        elif (x[0][i] + x[1][i] > 1):
            return 2
        # on n'automatise pas une usine qui n'existe pas
        elif (x[2][i] > x[0][i]):
            return 3
        #
        elif (x[0][x[3][i]] == 0 and x[1][i] == 1):
            return 4
        elif (x[1][x[3][i]] == 1):
            return 5
        elif (x[1][x[4][i]] + x[0][x[4][i]] != 1):
            return 6
    for i in range(nb_client):
        if (x[4][i] < 0):
            return 7
    return 0


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

def check_constraint(x):
    if nb_client!=len(x[4]):
        print('longueur')
        return False
    if nb_site!=len(x[0]) or nb_site!=len(x[1]) or nb_site!=len(x[2]) or nb_site!=len(x[3]):
        print('longueur')
        return False
    for i in range (nb_site) :
        # tout est positif
        if (x[0][i] < 0 or x[1][i] < 0 or x[2][i] < 0 or x[3][i] < 0):
            print('domain (<0 facility)')
            return False
        if (x[0][i] > 1 or x[1][i] > 1 or x[2][i] > 1):
            print('domain (>1 facility)')
            return False
        # 1 site est occupé par une seule usine
        elif (x[0][i] + x[1][i] > 1):
            print('multiple facilities in one place')
            return False
        # on n'automatise pas une usine qui n'existe pas
        elif (x[2][i] > x[0][i]) :
            print('no factory to automate')
            return False
        #
        elif (x[0][x[3][i]] == 0 and x[1][i] == 1) :
            print('unconnected distrib')
            return False
        elif (x[1][x[3][i]] == 1) :
            print('parent of facility is distrib')
            return False
        elif (x[1][x[4][i]] + x[0][x[4][i]] !=1) :
            print('0 or multiple parent facilities for client')
            return False
    for i in range(nb_client) :
        if (x[4][i] < 0) :
            print('domain (<0 client)')
            return False
    return True


def descente_locale_large(nb_sites, nb_client):
    # On construit une solution initiale
    x_init = [[0 for i in range (nb_sites-1)],[0 for i in range (nb_sites)],[0 for i in range (nb_sites)],[0 for i in range (nb_sites)],[nb_sites-1 for i in range(nb_client)]]
    x_init[0].append(1)
    if (check_constraint(x_init,nb_sites,nb_client) != 0):
        print("erreur",check_constraint(x_init,nb_sites,nb_client))
    count = 0
    while (count <= 500):
        x= x_init
        count += 1
        n_usine = random.randint(0,nb_sites-1)
        if (x[0][n_usine] == 0):
            x[0][n_usine] = 1
            for i in range (nb_client) :
                dist = siteClientDistances[0][i]
                for j in range (nb_sites):
                    if (x[0][j] == 1):
                        n_dist = siteClientDistances[j][i]
                        if (n_dist < dist):
                            dist = n_dist
                            x[4][i] = j
        if (total_cost(x_init) > total_cost(x)):
            x_init = x
    count = 0
    while (count <= 100):
        x = x_init
        count += 1
        hasard = random.randint(1,4)
        n_usine = random.randint(0, nb_sites - 1)
        if (hasard == 1):
            if (x[0][n_usine] == 1):
                x[0][n_usine] = 0
                x[1][n_usine] = 1
                for i in range (nb_sites):
                    dist=siteSiteDistances[0][i]
                    for j in range (nb_sites):
                        n_dist = siteSiteDistances[j][i]
                        if(n_dist < dist and x[0][j] == 1):
                            dist = n_dist
                            x[3][i] = j
        elif (hasard == 2):
            if (x[0][n_usine] == 1):
                x[2][n_usine] = 1
        elif (hasard == 3):
            if (x[0][n_usine] == 1):
                x[2][n_usine] = 0
        if (total_cost(x_init) > total_cost(x) and check_constraint(x) == 0):
            x_init = x
    return(x_init)
