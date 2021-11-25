import numpy as np


def heuristique1(parameters, clients, sites, siteSiteDistances, siteClientDistances):
    print("nb_clients = ", nb_client)
    print("nb_sites = ", nb_site)
    total_demand = 0
    for client in clients:
        demand = client["demand"]
        total_demand += demand
    min = 100000000000000000
    number_of_usine = total_demand / parameters["capacities"]["productionCenter"]
    for j in range(nb_site):
        # if la distance moyenne d'un site est plus petite que la moyenne on prend ce site
        dist_moy = np.abs(np.mean(siteClientDistances[:, j]))
        if (dist_moy < min):
            min = dist_moy
            j_choice_to_construct = j
    return 0
