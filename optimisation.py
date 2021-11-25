import numpy as np

def genere_sol_admissible(parameters,clients,sites,siteSiteDistances,siteClientDistances):
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
