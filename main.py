import random
import numpy as np
import json_reader as jr
from pulp import *
import json
from affichage import result

if __name__ == '__main__':
    file_name = "KIRO-medium.json"

    file_name_path = "instances/" + file_name
    file_name_sol = "sol-" + file_name
    file_name_sol_path = "solution/" + file_name_sol

    parameters, clients, sites, siteSiteDistances, siteClientDistances = jr.read_data(file_name_path)
    nb_client = len(clients)
    nb_site = len(sites)
    print("nb_clients = ", nb_client)
    print("nb_sites = ", nb_site)

    # Structure de x

    # [ (production)[liste de 0 et de 1 de taille nb_de_sites],
    #   (distribution)[liste de 0 et de 1 de taille nb_de_sites],
    #   (automat)[liste de 0 et de 1 de taille nb_de_sites],
    #   (parent)[liste d'indices de sites de prod de taille nb_sites],
    #   (parent des clients)[liste d'indices de sites de taille nb_client] ]

    # Contraintes sur la structure de x

    # production[i] + distribution[i] <=1
    # automat[i] <= production[i]
    # production[parent[i]] = 1 si distribution (qui existe !!!)
    # production[parent[i]] = 0 si production
    # distribution[parent[i]] = 0
    # production[client[i]] + distribution[client[i]] =1
    # tout >=0

# RESOLUTION PAR PLNE

# VARIABLES

# sites de construction
x_c = [LpVariable("x_construction_" + str(i), lowBound=0, upBound=1, cat=LpInteger) for i in range(nb_site)]
print("x_production :", x_c)
# sites de distribution
x_d = [LpVariable("x-distribution_" + str(i), lowBound=0, upBound=1, cat=LpInteger) for i in range(nb_site)]
print("x_distribution :", x_d)
# automatisation
x_a = [LpVariable("x_auto_" + str(i), lowBound=0, upBound=1, cat=LpInteger) for i in range(nb_site)]
print("x_automatisation :", x_a)
# parents
x_p = [[LpVariable("x_parent_distribution_" + str(i)+ "_"+ str(j), lowBound=0, upBound=1, cat=LpInteger) for i in
        range(nb_site)] for j in range(nb_site)]
print("x_parent :", x_p)
# clients
x_cl = [[LpVariable("x_parent_client_" + str(i)+ "_" + str(j), lowBound=0, upBound=1, cat=LpInteger) for i in range(nb_site)]
        for j in range(nb_client)]
print("x_client :", x_cl)

# PROBLEME

prob = LpProblem(name='facility_location', sense=LpMinimize)

# CONTRAINTES

# Au plus un batiment par site
for id_site in range(nb_site):
    prob += (x_c[id_site] + x_d[id_site] <= 1)
# Automatisation seulement sur les centres de production
for id_site in range(nb_site):
    prob += (x_a[id_site] <= x_c[id_site])
# Parents des centres de distribution (unicité)
for id_site in range(nb_site):
    prob += (lpSum(x_p[id_site]) == 1)
# Parents (validité du parent)
for id_site in range(nb_site):
    for id_parent in range(nb_site):
        prob += (x_p[id_site][id_parent] <= x_c[id_parent])
# Clients (unicité)
for id_client in range(nb_client):
    prob += (lpSum(x_cl[id_client]) == 1)
# Clients (validité du parent)
for id_client in range(nb_client):
    for id_parent in range(nb_site):
        prob += (x_cl[id_client][id_parent] <= x_c[id_parent] + x_d[id_parent])

# FONCTION OBJECTIF

# building costs
objective = lpSum(x_c) * parameters["buildingCosts"]["productionCenter"] + \
            lpSum(x_a) * parameters["buildingCosts"]["automationPenalty"] + \
            lpSum(x_d) * parameters["buildingCosts"]["distributionCenter"]

# production costs



prob.setObjective(objective)

# SOLVEUR

prob.solve()

result(x_c, x_d, x_a, x_p, x_cl, nb_site, nb_client)
