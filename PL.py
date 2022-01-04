from pulp import *
import numpy as np

def check_constraint(X, nb_site, nb_client):
    nb_error = 0
    check = True
    # Au plus un batiment par site
    for id_site in range(nb_site):
        if not (X[0][id_site] + X[1][id_site] <= 1):
            print("Il y a plus d'un batiment sur un des sites " + str(id_site + 1))
            nb_error += 1
            check = False
    # Automatisation seulement sur les centres de production
    for id_site in range(nb_site):
        if not (X[2][id_site] <= X[0][id_site]):
            print("mauvaise automatisation " + str(id_site + 1))
            nb_error += 1
            check = False
    # Parents des centres de distribution (~unicité)
    for id_site in range(nb_site):
        if not (np.sum(X[3][id_site]) == X[1][id_site]):
            print("Parents non unique (centres de distribution) " + str(id_site + 1))
            nb_error += 1
            check = False
    # Parents (validité du parent)
    for id_site in range(nb_site):
        for id_parent in range(nb_site):
            if not (X[3][id_site][id_parent] <= X[0][id_parent]):
                print("Parents incompatibles (centres de distribution) --> site : " + str(
                    id_site + 1) + " --> parent : " + str(id_parent + 1))
                nb_error += 1
                check = False
    # Clients (unicité)
    for id_client in range(nb_client):
        if not (np.sum(X[4][id_client]) == 1):
            print("Parents non unique (clients) " + str(id_client + 1))
            nb_error += 1
            check = False
    # Clients (validité du parent)
    for id_client in range(nb_client):
        for id_parent in range(nb_site):
            if not (X[4][id_client][id_parent] <= X[0][id_parent] + X[1][id_parent]):
                print("Parents incompatibles (clients) --> client : " + str(id_client + 1) + " --> parent : " + str(
                    id_parent + 1))
                nb_error += 1
                check = False
    print("nombre d'erreurs ... " + str(nb_error))
    return check

def pre_traitement_super_client(set_super_client : list, parameters, clients, sites, siteSiteDistances, siteClientDistances):
    new_clients = []
    new_sites = sites
    new_siteSiteDistances = siteSiteDistances
    new_siteClientDistances = [[] for i in range (len(sites))]
    for super_client in set_super_client:
        # print(super_client.id)
        new_clients.append(
            {"id": super_client.id, "demand": super_client.demand, "coordinates": super_client.coordinates})
        try:
            for i in range(len(sites)):
                new_siteClientDistances[i].append(siteClientDistances[i][super_client.id - 1])
        except:
            cluster_id_list = []
            for i in range(len(set_super_client)):
                cluster_id_list.append(set_super_client[i].id)
            cluster_id_list.sort()
            for i in range(len(sites)):
                new_siteClientDistances[i].append(siteClientDistances[i][cluster_id_list.index(super_client.id)])
    return new_clients, new_sites, new_siteSiteDistances, new_siteClientDistances


def post_traitement_super_client(X, set_super_client, clients, sites, siteSiteDistances, siteClientDistances):
    check_constraint(X,len(X[0]),len(X[4]))
    nb_cl = len(clients)
    nb_sit = len(sites)
    production = X[0]
    distribution = X[1]
    auto = X[2]
    parent = X[3]
    clie = [[] for j in range(nb_cl)]
    k = 0
    j = 0
    try:
        for super_client in set_super_client:
            clie[super_client.id - 1] = X[4][k]
            for child in super_client.children:
                clie[child - 1] = clie[super_client.id - 1]
            k += 1

    except:
        k = 0
        cluster_id_list = []
        for i in range(len(set_super_client)):
            cluster_id_list.append(set_super_client[i].id)
            for child in set_super_client[i].children:
                cluster_id_list.append(child)

        cluster_id_list.sort()

        for super_client in set_super_client:
            # print(cluster_id_list.index(super_client.id))
            clie[cluster_id_list.index(super_client.id)] = X[4][k]


            for child in super_client.children:
                clie[cluster_id_list.index(child)] = clie[cluster_id_list.index(super_client.id)]
                j += 1
            k += 1
    return [production,distribution,auto,parent,clie]





def solution_pl(parameters, cli, sit, siteSit, siteCli, set_super_client=None):

    old_clients = cli
    old_sites = sit
    old_siteSiteDistances = siteSit
    old_siteClientDistances = siteCli


def solution_pl(parameters, clients, sites, siteSiteDistances, siteClientDistances, fix_c=None, fix_d=None \
                , fix_a=None, fix_p=None, fix_cl=None):
    if set_super_client != None:
        clients, sites, siteSiteDistances, siteClientDistances = pre_traitement_super_client(set_super_client,
                                                                                             parameters, old_clients,
                                                                                             old_sites,
                                                                                             old_siteSiteDistances,
                                                                                             old_siteClientDistances)
    else :
        clients, sites, siteSiteDistances, siteClientDistances = old_clients, old_sites, old_siteSiteDistances, old_siteClientDistances

    nb_site = len(sites)
    nb_client = len(clients)

    # sites de construction
    x_c = [LpVariable("x_construction_" + str(i), lowBound=0, upBound=1, cat=LpInteger) for i in range(nb_site)]
    # sites de distribution
    x_d = [LpVariable("x-distribution_" + str(i), lowBound=0, upBound=1, cat=LpInteger) for i in range(nb_site)]
    # automatisation
    x_a = [LpVariable("x_auto_" + str(i), lowBound=0, upBound=1, cat=LpInteger) for i in range(nb_site)]
    # parents
    x_p = [[LpVariable("x_parent_distribution_" + str(i) + "_" + str(j), lowBound=0, upBound=1, cat=LpInteger) for i in
            range(nb_site)] for j in range(nb_site)]
    # clients
    x_cl = [[LpVariable("x_parent_client_" + str(i) + "_" + str(j), lowBound=0, upBound=1, cat=LpInteger) for i in
             range(nb_site)]
            for j in range(nb_client)]

    if(fix_c != None):
        for index, val_fix in fix_c:
            x_c[index].setInitialValue(val_fix)
            x_c[index].fixValue()

    if (fix_c != None):
        for index, val_fix in fix_c:
            x_c[index].setInitialValue(val_fix)
            x_c[index].fixValue()

    if (fix_d != None):
        for index, val_fix in fix_d:
            x_d[index].setInitialValue(val_fix)
            x_d[index].fixValue()

    if (fix_a != None):
        for index, val_fix in fix_a:
            x_a[index].setInitialValue(val_fix)
            x_a[index].fixValue()

    if (fix_p != None):
        for index, val_fix in fix_p:
            x_p[index[0]][index[1]].setInitialValue(val_fix)
            x_p[index[0]][index[1]].fixValue()

    if (fix_cl != None):
        for index, val_fix in fix_cl:
            x_cl[index[0]][index[1]].setInitialValue(val_fix)
            x_cl[index[0]][index[1]].fixValue()

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
        [LpVariable("z_client_distribution_" + str(i) + "_" + str(j), lowBound=0, upBound=1, cat=LpInteger) for i in
         range(nb_site)] for j in range(nb_client)]
    for id_client in range(nb_client):
        for id_site in range(nb_site):
            prob += z_client_distribution[id_client][id_site] <= x_cl[id_client][id_site]
            prob += z_client_distribution[id_client][id_site] <= x_d[id_site]
            prob += z_client_distribution[id_client][id_site] >= x_cl[id_client][id_site] + x_d[id_site] - 1

    z_client_auto = [
        [LpVariable("z_client_auto_" + str(i) + "_" + str(j), lowBound=0, upBound=1, cat=LpInteger) for i in
         range(nb_site)] for j in range(nb_client)]
    for id_client in range(nb_client):
        for id_site in range(nb_site):
            prob += z_client_auto[id_client][id_site] <= x_cl[id_client][id_site]
            prob += z_client_auto[id_client][id_site] <= x_a[id_site]
            prob += z_client_auto[id_client][id_site] >= x_cl[id_client][id_site] + x_a[id_site] - 1

    z_client_parent = [
        [[LpVariable("z_client_parent_" + str(i) + "_" + str(j) + "_" + str(k), lowBound=0, upBound=1, cat=LpInteger)
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
        [LpVariable("z_production_client_" + str(i) + "_" + str(j), lowBound=0, upBound=1, cat=LpInteger) for i in
         range(nb_client)] for j in range(nb_site)]
    for id_site in range(nb_site):
        for id_client in range(nb_client):
            prob += z_production_client[id_site][id_client] <= x_cl[id_client][id_site]
            prob += z_production_client[id_site][id_client] <= x_p[id_site]
            prob += z_production_client[id_site][id_client] >= x_p[id_site] + x_cl[id_client][id_site] - 1

    z_client_parent_auto = [[[LpVariable("z_client_parent_auto_" + str(i) + "_" + str(j) + "_" + str(k), lowBound=0,
                                         upBound=1, cat=LpInteger) for i in range(nb_site)] for j in range(nb_site)] for
                            k in range(nb_client)]
    for id_client in range(nb_client):
        for id_site_j in range(nb_site):
            for id_site_k in range(nb_site):
                prob += z_client_parent_auto[id_client][id_site_j][id_site_k] <= z_client_parent[id_client][id_site_j][
                    id_site_k]
                prob += z_client_parent_auto[id_client][id_site_j][id_site_k] <= x_a[id_site_k]
                prob += z_client_parent_auto[id_client][id_site_j][id_site_k] >= z_client_parent[id_client][id_site_j][
                    id_site_k] + x_a[id_site_k] - 1

    non_negative_part = [LpVariable("non_negative_part_" + str(i), lowBound=0, cat=LpInteger) for i in range(nb_site)]
    for id_site in range(nb_site):
        somme = 0
        for id_client in range(nb_client):
            somme += clients[id_client]["demand"] * z_production_client[id_site][id_client]
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
            somme += parameters["productionCosts"]["distributionCenter"] * z_client_distribution[i][j] - \
                     parameters["productionCosts"]["automationBonus"] * z_client_auto[i][j]
            for k in range(nb_site):
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

    prob.solve(PULP_CBC_CMD(msg=True, warmStart=True, options= ['maxsol 1']))

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

    X_solution = [x_production, x_distribution,x_auto, x_parent, x_client]

    if set_super_client != None:
        X_solution = post_traitement_super_client(X_solution, set_super_client, old_clients, old_sites, old_siteSiteDistances,
                                         old_siteClientDistances)
    return X_solution
