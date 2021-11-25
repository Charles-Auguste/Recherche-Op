import numpy as np

def genere_sol_admissible(parameters,clients,sites,sitrSiteDistances,siteClientDistances):
    x = [[0 for i in range(nb_site)], [0 for i in range(nb_site)], [0 for i in range(nb_site)],
         [0 for i in range(nb_site)], [0 for i in range(nb_client)]]

def heuristique1(parameters, clients, sites, siteSiteDistances, siteClientDistances):
    nb_client = len(clients)
    nb_site = len(sites)
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
    x[0][j]
    return 0
