import pulp
import json
import json_reader as jr


if __name__=='__main__':

    file_name = "KIRO-tiny.json"
    parameters, clients, sites, siteSiteDistances, siteClientDistances = jr.read_data(file_name)

    # Structure de x

    # [ (production)[liste de 0 et de 1 de taille nb_de_sites],
    #   (distribution)[liste de 0 et de 1 de taille nb_de_sites],
    #   (automat)[liste de 0 et de 1 de taille nb_de_sites],
    #   (parent)[liste d'id de sites de prod de taille nb_sites],
    #   (client)[liste d'id de sites de taille nb_client]

    # Contraintes sur la structure de x

    # production[i] + distribution[i] <=1
    # automat[i] <= production[i]
    # production[parent[i]] = 1
    # distribution[parent[i]] = 0
    # production[client[i]] + distribution[client[i]] =1
    # tout >=0

    nb_client = len(clients)
    nb_site = len(sites)

    def building_cost (s,x) :
        """s est le numero du site """
        pass

    def production_cost (i,x) :
        pass

    def routing_cost (i,x) :
        pass

    def capacity_cost (s,x) :
        pass

    print("nb_clients = ",nb_client)
    print("nb_sites = ", nb_site)






