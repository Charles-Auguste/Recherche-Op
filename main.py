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
    #   (parent)[liste d'indices de sites de prod de taille nb_sites],
    #   (parent des clients)[liste d'indices de sites de taille nb_client] ]

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
        """i est le numero du client """
        # if parent = producter
        if(x[0][x[5][i-1]] == 1):
            # i+1 car les id start a 0 et nos listes a 0
            # x[3][x[5][i-1]] producter automatise?
            auto = x[2][x[4][i-1]]
            cost = clients[i-1]["demand"]*parameters["productionCosts"]["productionCenter"]-auto*parameters["productionCosts"]["automationBonus"]
            return cost
        # if parent = distrib
        elif(x[1][x[4][i-1]] == 1):
            # x[0][x[4][x[5][i-1]]] parent du distrib automatise?
            auto = x[0][x[3][x[4][i-1]]]
            cost = clients[i - 1]["demand"] * parameters["productionCosts"]["productionCenter"] - auto * parameters["productionCosts"]["automationBonus"] + parameters["productionCosts"]["distributionCenter"]
            return cost
        else:
            return float('inf')

    def routing_cost (i,x) :
        '''DANGER: On suppose que les clients sont ordonnés dans l'ordre des indices dans clients
        i: numéro du client
        x: solution au format liste de liste décrit plus haut'''
        if x[0][i-1]:
            return parameters["routingCosts"]["secondary"]*(siteClientDistances[x[4][i-1]][i-1])
        elif x[1][i-1]:
            return clients[i-1]["demand"]*\
                   (parameters["routingCosts"]["primary"]*siteClientDistances[x[4][i-1]][x[3][x[4][i-1]]]+
                   parameters["routingCosts"]["secondary"]*siteClientDistances[x[4][i-1]][i-1])
        else:
            return float('inf')

    def capacity_cost (s,x) :
        pass

    def total_cost(x):
        for s in range(1,nb_site+1):
            return


    print("nb_clients = ",nb_client)
    print("nb_sites = ", nb_site)






