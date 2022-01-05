#################################################################
# Calcul des coûts
# Authors : Charles-Auguste Gourio, Thomas Risola, Michel Senegas
# Date : 01/12/2021
#################################################################

def building_cost(x, parameters, nb_site):
    cost: int = 0
    for i in range(nb_site):
        cost += x[0][i] * parameters["buildingCosts"]["productionCenter"] + \
                x[1][i] * parameters["buildingCosts"]["distributionCenter"] + \
                x[2][i] * parameters["buildingCosts"]["automationPenalty"]
    return cost


def production_cost(x, parameters, clients, nb_client, nb_site):
    cost = 0
    for i in range(nb_client):
        cost += clients[i]["demand"] * parameters["productionCosts"]["productionCenter"]
        for k in range(nb_site):
            if x[4][i][k] * x[1][k]:
                cost += clients[i]["demand"] * parameters["productionCosts"]["distributionCenter"]
                for k2 in range(nb_site):
                    if x[3][k][k2] * x[2][k2]:
                        cost -= clients[i]["demand"] * parameters["productionCosts"]["automationBonus"]
            else:
                if x[4][i][k] * x[2][k]:
                    cost -= clients[i]["demand"] * parameters["productionCosts"]["automationBonus"]
    return cost


def routing_cost(x, parameters, clients, siteClientDistances, siteSiteDistances, nb_client, nb_site):
    cost = 0
    for i in range(nb_client):
        for k in range(nb_site):
            if x[4][i][k] * x[1][k]:
                cost += clients[i]["demand"] * parameters["routingCosts"]["secondary"] * siteClientDistances[k][i]
                for k2 in range(nb_site):
                    if x[3][k][k2]:
                        cost += clients[i]["demand"] * parameters["routingCosts"]["primary"] * siteClientDistances[k2][
                            k]
            elif x[4][i][k] * x[0][k]:
                cost += clients[i]["demand"] * parameters["routingCosts"]["secondary"] * siteClientDistances[k][i]
    return cost

def capacity_cost(x, parameters, clients, nb_client, nb_site):
    cost = 0
    for i in range(nb_site):
        if x[0][i] :
            sum_to_i = 0
            for k in range(nb_client):
                if x[4][k][i] :
                    sum_to_i += clients[k]["demand"]
            cost += max(0,parameters["capacityCost"]*(sum_to_i - (parameters["capacities"]["productionCenter"] +x[2][i] * parameters["capacities"]["automationBonus"])))
    return cost

def total_cost(x, parameters, clients, sites, siteSiteDistances, siteClientDistances):
    nb_client = len(clients)
    nb_site = len(sites)
    cost = 0
    cost += building_cost(x,parameters,nb_site)
    cost += production_cost(x,parameters,clients,nb_client,nb_site)
    cost += routing_cost(x,parameters,clients,siteClientDistances,siteSiteDistances,nb_client,nb_site)
    cost += capacity_cost(x,parameters,clients,nb_client,nb_site)
    print("building cost : ", building_cost(x,parameters,nb_site)/10000)
    print("production cost : ", production_cost(x,parameters,clients,nb_client,nb_site) / 10000)
    print("routing cost : ", routing_cost(x,parameters,clients,siteClientDistances,siteSiteDistances,nb_client,nb_site) / 10000)
    print("capacity cost : ", capacity_cost(x,parameters,clients,nb_client,nb_site) / 10000)
    return cost
