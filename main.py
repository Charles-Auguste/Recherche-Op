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

    def building_cost (s,x) :
        """s est le numero du site """
        if (x[0][s-1] == 1) :
            return parameters["buildingCosts"]["productionCenter"] + x[2][s-1] * parameters["buildingCosts"]["automationPenalty"]
        elif(x[1][s-1] == 1) :
            return parameters["buildingCosts"]["distributionCenter"]
        else :
            return 0

    def production_cost (i,x) :
        """i est le numero du client """
        # if parent = producter
        if(x[0][x[4][i-1]] == 1):
            # i+1 car les id start a 0 et nos listes a 0
            # x[2][x[4][i-1]] producter automatise?
            auto = x[2][x[4][i-1]]
            cost = clients[i-1]["demand"]*(parameters["productionCosts"]["productionCenter"]-auto*parameters["productionCosts"]["automationBonus"])
            return cost
        # if parent = distrib
        elif(x[1][x[4][i-1]] == 1):
            # x[2][x[3][x[4][i-1]]] parent du distrib automatise?
            auto = x[2][x[3][x[4][i-1]]]
            cost = clients[i - 1]["demand"] * (parameters["productionCosts"]["productionCenter"] - auto * parameters["productionCosts"]["automationBonus"] + parameters["productionCosts"]["distributionCenter"])
            return cost
        else:
            return float('inf')

    def routing_cost (i,x) :
        '''DANGER: On suppose que les clients sont ordonnés dans l'ordre des indices dans clients
        i: numéro du client
        x: solution au format liste de liste décrit plus haut'''
        if x[0][x[4][i-1]]:
            return clients[i-1]["demand"]*parameters["routingCosts"]["secondary"]*(siteClientDistances[x[4][i-1]][i-1])
        elif x[1][x[4][i-1]]:
            return clients[i-1]["demand"]*\
                   (parameters["routingCosts"]["primary"]*siteClientDistances[x[4][i-1]][x[3][x[4][i-1]]]+
                   parameters["routingCosts"]["secondary"]*siteClientDistances[x[4][i-1]][i-1])
        else:
            return float('inf')

    def capacity_cost (s,x) :
        if (x[0][s-1] == 1):
            value = 0
            for i in range (nb_client):
                if(x[4][i-1] == s or x[3][x[4][i-1]] == s):
                    value += clients[i-1]["demand"]
            value -= (parameters["capacities"]["productionCenter"] + x[2][s-1] * parameters["capacities"]["automationBonus"])
            value_max = max(0,value * parameters["capacityCost"])
            return value_max
        else:
            return 0

    def total_cost(x):
        cost = 0
        for site in sites:
            s = site["id"]
            cost += building_cost(s,x)+capacity_cost(s,x)
        for client in clients:
            i = client["id"]
            cost += production_cost(i,x) + routing_cost(i,x)
        return cost


    print("nb_clients = ",nb_client)
    print("nb_sites = ", nb_site)


    def check_constraint(x):
        if nb_client!=len(x[4]):
            print('longueur')
            return False
        if nb_site!=len(x[0]) or nb_site!=len(x[1]) or nb_site!=len(x[2]) or nb_site!=len(x[3]):
            print('longueur')
            return False
        for i in range (nb_site) :
            # tout est positif
            if (x[0][i] < 0 or x[1][i] < 0 or x[2][i] < 0 or x[3][i] < 0):
                print('domain (<0 facility)')
                return False
            if (x[0][i] > 1 or x[1][i] > 1 or x[2][i] > 1):
                print('domain (>1 facility)')
                return False
            # 1 site est occupé par une seule usine
            elif (x[0][i] + x[1][i] > 1):
                print('multiple facilities in one place')
                return False
            # on n'automatise pas une usine qui n'existe pas
            elif (x[2][i] > x[0][i]) :
                print('no factory to automate')
                return False
            #
            elif (x[0][x[3][i]] == 0 and x[1][i] == 1) :
                print('unconnected distrib')
                return False
            elif (x[1][x[3][i]] == 1) :
                print('parent of facility is distrib')
                return False
            elif (x[1][x[4][i]] + x[0][x[4][i]] !=1) :
                print('0 or multiple parent facilities for client')
                return False
        for i in range(nb_client) :
            if (x[4][i] < 0) :
                print('domain (<0 client)')
                return False
        return True

    x = op.genere_sol_admissible(clients,sites)
    print(check_constraint(x))
    print(total_cost(x))




