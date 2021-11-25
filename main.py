import pulp
import json
import json_reader as jr
import numpy as np
import optimisation as op


if __name__=='__main__':

    parameters, clients, sites, siteSiteDistances, siteClientDistances = jr.read_data(op.file_name)

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

    nb_client = len(clients)
    nb_site = len(sites)

    print("nb_clients = ",nb_client)
    print("nb_sites = ", nb_site)

    x = op.genere_sol_admissible(clients,sites)
    print(op.check_constraint(x))
    print(op.total_cost(x))




