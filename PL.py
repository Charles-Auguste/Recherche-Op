from pulp import *

def solution_pl(parameters, clients, sites, siteSiteDistances, siteClientDistances, RL= False):
    if RL:
        var_cat = LpVariable
    else:
        var_cat = LpInteger
    nb_site = len(sites)
    nb_client = len(clients)

    # sites de construction
    x_c = [LpVariable("x_construction_" + str(i), lowBound=0, upBound=1, cat=var_cat) for i in range(nb_site)]
    # sites de distribution
    x_d = [LpVariable("x-distribution_" + str(i), lowBound=0, upBound=1, cat=var_cat) for i in range(nb_site)]
    # automatisation
    x_a = [LpVariable("x_auto_" + str(i), lowBound=0, upBound=1, cat=var_cat) for i in range(nb_site)]
    # parents
    x_p = [[LpVariable("x_parent_distribution_" + str(i) + "_" + str(j), lowBound=0, upBound=1, cat=var_cat) for i in
            range(nb_site)] for j in range(nb_site)]
    # clients
    x_cl = [[LpVariable("x_parent_client_" + str(i) + "_" + str(j), lowBound=0, upBound=1, cat=var_cat) for i in
             range(nb_site)]
            for j in range(nb_client)]

    prob = LpProblem(name='facility_location', sense=LpMinimize)

    # Au plus un batiment par site
    for id_site in range(nb_site):
        prob += (x_c[id_site] + x_d[id_site] <= 1)
    # Automatisation seulement sur les centres de production
    for id_site in range(nb_site):
        prob += (x_a[id_site] <= x_c[id_site])
    # Parents des centres de distribution (~unicité)
    for id_site in range(nb_site):
        prob += (lpSum(x_p[id_site]) == x_d[id_site])
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

    # produits

    z_client_distribution = [
        [LpVariable("z_client_distribution_" + str(i) + "_" + str(j), lowBound=0, upBound=1, cat=var_cat) for i in
         range(nb_site)] for j in range(nb_client)]
    for id_client in range(nb_client):
        for id_site in range(nb_site):
            prob += z_client_distribution[id_client][id_site] <= x_cl[id_client][id_site]
            prob += z_client_distribution[id_client][id_site] <= x_d[id_site]
            prob += z_client_distribution[id_client][id_site] >= x_cl[id_client][id_site] + x_d[id_site] - 1

    z_client_auto = [
        [LpVariable("z_client_auto_" + str(i) + "_" + str(j), lowBound=0, upBound=1, cat=var_cat) for i in
         range(nb_site)] for j in range(nb_client)]
    for id_client in range(nb_client):
        for id_site in range(nb_site):
            prob += z_client_auto[id_client][id_site] <= x_cl[id_client][id_site]
            prob += z_client_auto[id_client][id_site] <= x_a[id_site]
            prob += z_client_auto[id_client][id_site] >= x_cl[id_client][id_site] + x_a[id_site] - 1

    z_client_parent = [
        [[LpVariable("z_client_parent_" + str(i) + "_" + str(j) + "_" + str(k), lowBound=0, upBound=1, cat=var_cat)
          for i in
          range(nb_site)] for j in range(nb_site)] for k in range(nb_client)]
    for id_client in range(nb_client):
        for id_site_j in range(nb_site):
            for id_site_i in range(nb_site):
                prob += z_client_parent[id_client][id_site_i][id_site_j] <= x_cl[id_client][id_site_i]
                prob += z_client_parent[id_client][id_site_i][id_site_j] <= x_p[id_site_i][id_site_j]
                prob += z_client_parent[id_client][id_site_i][id_site_j] >= x_cl[id_client][id_site_i] + x_p[id_site_i][
                    id_site_j] - 1

    z_production_client = [
        [LpVariable("z_production_client_" + str(i) + "_" + str(j), lowBound=0, upBound=1, cat=var_cat) for i in
         range(nb_client)] for j in range(nb_site)]
    for id_site in range(nb_site):
        for id_client in range(nb_client):
            prob += z_production_client[id_site][id_client] <= x_cl[id_client][id_site]
            prob += z_production_client[id_site][id_client] <= x_p[id_site]
            prob += z_production_client[id_site][id_client] >= x_p[id_site] + x_cl[id_client][id_site] - 1

    z_client_parent_auto = [[[LpVariable("z_client_parent_auto_" + str(i) + "_" + str(j) + "_" + str(k), lowBound=0,
                                         upBound=1, cat=var_cat) for i in range(nb_site)] for j in range(nb_site)] for
                            k in range(nb_client)]
    for id_client in range(nb_client):
        for id_site_j in range (nb_site):
            for id_site_k in range (nb_site):
                prob += z_client_parent_auto[id_client][id_site_j][id_site_k] <= z_client_parent[id_client][id_site_j][id_site_k]
                prob += z_client_parent_auto[id_client][id_site_j][id_site_k] <= x_a[id_site_k]
                prob += z_client_parent_auto[id_client][id_site_j][id_site_k] >= z_client_parent[id_client][id_site_j][
                    id_site_k] + x_a[id_site_k] - 1

    non_negative_part = [LpVariable("non_negative_part_" + str(i), lowBound=0, cat=var_cat) for i in range(nb_site)]
    for id_site in range(nb_site):
        somme = 0
        for id_client in range(nb_client):
            somme += clients[id_client]["demand"] * z_production_client[id_site][id_client]
        somme -= (parameters["capacities"]["productionCenter"] + x_a[id_site] * parameters["capacities"]["automationBonus"])
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
            somme += parameters["productionCosts"]["distributionCenter"] * z_client_distribution[i][j] - parameters["productionCosts"]["automationBonus"] * z_client_auto[i][j]
            for k in range (nb_site):
                somme -= parameters["productionCosts"]["automationBonus"] * z_client_parent_auto[i][j][k]
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
                somme2 += parameters["routingCosts"]["primary"] * z_client_parent[i][j][k] * siteSiteDistances[j][k]
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

    x_production = []
    x_distribution = []
    x_auto = []
    x_parent = [[0 for i in range(nb_site)] for j in range(nb_site)]
    x_client = [[0 for i in range(nb_site)] for j in range(nb_client)]
    for i in range(nb_site):
        x_production.append(x_c[i].value())
        x_distribution.append(x_d[i].value())
        x_auto.append(x_a[i].value())
    for i in range(nb_site):
        for j in range(nb_site):
            x_parent[i][j] = x_p[i][j].value()
    for i in range(nb_client):
        for j in range(nb_site):
            x_client[i][j] = x_cl[i][j].value()

    return [x_production, x_distribution,x_auto, x_parent, x_client]
