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
    #   (client)[liste d'id de sites de taille nb_client] ]

    # Contraintes sur la structure de x

    # production[i] + distribution[i] <=1
    # automat[i] <= production[i]
    # production[parent[i]] = 1
    # distribution[parent[i]] = 0
    # production[client[i]] + distribution[client[i]] =1
    # tout >=0

    def building_cost (s,x) :
        pass

    def production_cost (i,x) :
        pass

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

    def capacity_cost (s,x) :
        pass








