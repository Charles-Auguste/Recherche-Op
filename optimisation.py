#################################################################
# optimisation.py
# Authors : Charles-Auguste Gourio, Thomas Risola, Michel Senegas
# Date : 01/12/2021
#################################################################

import random
import numpy as np
import pulp
from main import parameters,clients,siteSiteDistances,siteClientDistances,sites,nb_site,nb_client


def building_cost(s, x):
    """gives the building cost in the site s (s is the id of the site)"""
    if x[0][s - 1] == 1:
        return parameters["buildingCosts"]["productionCenter"] + x[2][s - 1] * parameters["buildingCosts"][
            "automationPenalty"]
    elif x[1][s - 1] == 1:
        return parameters["buildingCosts"]["distributionCenter"]
    else:
        return 0


def production_cost(i, x):
    """gives the production cost for a given client i (i is the iod of the client)"""
    # if parent = production
    if x[0][x[4][i - 1]] == 1:
        # i+1 car les id start a 0 et nos listes a 0
        # x[2][x[4][i-1]] producter automatise?
        auto = x[2][x[4][i - 1]]
        cost = clients[i - 1]["demand"] * (
                    parameters["productionCosts"]["productionCenter"] - auto * parameters["productionCosts"][
                        "automationBonus"])
        return cost
    # if parent = distribution
    elif x[1][x[4][i - 1]] == 1:
        # x[2][x[3][x[4][i-1]]] parent du distrib automatise?
        auto = x[2][x[3][x[4][i - 1]]]
        cost = clients[i - 1]["demand"] * (
                    parameters["productionCosts"]["productionCenter"] - auto * parameters["productionCosts"][
                        "automationBonus"] + parameters["productionCosts"]["distributionCenter"])
        return cost
    else:
        return float('inf')


def routing_cost(i, x):
    """DANGER: On suppose que les clients sont ordonnés dans l'ordre des indices dans clients
    i: numéro du client
    x: solution au format liste de liste décrit plus haut"""
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
    if x[0][s - 1] == 1:
        value = 0
        for i in range(nb_client):
            if x[4][i - 1] == s or x[3][x[4][i - 1]] == s:
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


