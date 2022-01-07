from pulp import *
import numpy as np

def solution_pl(parameters, cli, sit, siteSit, siteCli, X):

    old_clients = cli
    old_sites = sit
    old_siteSiteDistances = siteSit
    old_siteClientDistances = siteCli

    clients, sites, siteSiteDistances, siteClientDistances = old_clients, old_sites, old_siteSiteDistances, old_siteClientDistances

    nb_site = len(sites)
    nb_client = len(clients)


    x_cl = [[LpVariable("x_parent_client_" + str(i) + "_" + str(j), lowBound=0, upBound=1, cat=LpInteger) for i in
             range(nb_site)]
            for j in range(nb_client)]

    x_c = X[0]
    x_d = X[1]
    x_a = X[2]
    x_p = X[3]

    prob = LpProblem(name='facility_location', sense=LpMinimize)

    # Clients (unicité)
    for id_client in range(nb_client):
        prob += (lpSum(x_cl[id_client]) == 1)

    non_negative_part = [LpVariable("non_negative_part_" + str(i), lowBound=0, cat=LpInteger) for i in range(nb_site)]
    for id_site in range(nb_site):
        somme = 0
        for id_client in range(nb_client):
            somme += clients[id_client]["demand"] * x_cl[id_client][id_site] * x_c[id_site]
        somme -= (parameters["capacities"]["productionCenter"] + x_a[id_site] * parameters["capacities"][
            "automationBonus"])
        prob += non_negative_part[id_site] >= somme

    # Objectif

    objective = 0
    # construction
    for i in range(nb_site):
        objective += parameters["buildingCosts"]["productionCenter"] * x_c[i] + parameters["buildingCosts"][
            "distributionCenter"] * x_d[i] + parameters["buildingCosts"]["automationPenalty"] * x_a[i]
    # production
    for i in range(nb_client):
        somme = 0
        for j in range(nb_site):
            somme += parameters["productionCosts"]["distributionCenter"] * x_cl[i][j] * x_d[j]  - parameters["productionCosts"]["automationBonus"] * x_c[j]*x_a[j]
            for k in range(nb_site):
                somme -= parameters["productionCosts"]["automationBonus"] * x_cl[i][j] * x_d[j]* x_p[j][k] * x_a[k]
        somme += parameters["productionCosts"]["productionCenter"]
        somme *= clients[i]["demand"]
        objective += somme
    # transport
    for i in range(nb_client):
        somme = 0
        for j in range(nb_site):
            somme += parameters["routingCosts"]["secondary"] * x_cl[i][j] * siteClientDistances[j][i]
            somme2 = 0
            for k in range(nb_site):
                somme2 += parameters["routingCosts"]["primary"] * x_cl[i][j]*x_p[j][k] * siteSiteDistances[j][k]
            somme += somme2
        somme *= clients[i]["demand"]
        objective += somme
    # capacite
    somme = 0
    for i in range(nb_site):
        somme += parameters["capacityCost"] * non_negative_part[i]
    objective += somme

    prob.objective = objective

    # SOLVEUR

    prob.solve(PULP_CBC_CMD())

    # Solutions

    x_client = [[0 for i in range(nb_site)] for j in range(nb_client)]
    for i in range(nb_client):
        for j in range(nb_site):
            x_client[i][j] = x_cl[i][j].value()

    X_client = x_client

    return X_client