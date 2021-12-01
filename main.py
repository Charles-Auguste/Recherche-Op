import random
import numpy as np
import json_reader as jr
import pulp
import json


if __name__=='__main__':

    file_name = "KIRO-large.json"

    file_name_path = "instances/" + file_name
    file_name_sol = "sol-" + file_name
    file_name_sol_path = "solution/" + file_name_sol

    parameters, clients, sites, siteSiteDistances, siteClientDistances = jr.read_data(file_name_path)
    nb_client = len(clients)
    nb_site = len(sites)
    print("nb_clients = ",nb_client)
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





