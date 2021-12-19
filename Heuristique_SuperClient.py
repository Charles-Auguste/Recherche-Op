######################################
# Heuristique du Super Client
# Authors : Charles-Auguste Gourio
# Date : 10/12/2021
######################################

"""
Dans le problème proposé par Air Liquide, les clients sont regroupés entre eux. L'odée derrière cette heuristique
est de reproduire la manipulation pour creer au sein des grand problèmes comme "kiro-large" des "superclients"
regroupant plusieurs autres clients.



Quels sont les caractéristiques de ces clients ?
________________________________________________________________________________________________________________________
Soit S un super client composé des clients (cl_1,cl_2,...cl_n)
où cl1 est le père de tous les clients
S possède un id -> celui de cl_1
          une demande -> la somme des demandes des cl_i
          des coordonnées -> les coordonnées de cl_1
          des enfants -> une liste des id de cl_2,cl_3,...cl_n



Comment construire des supers clients ?
________________________________________________________________________________________________________________________
On utilise un algorithme glouton dont le détail est donné ci-dessous :

S = ensemble des superclients
C = ensemble des clients
Tant que C non vide :
    Prendre un client cl dans C (aléatoirement) et le retirer de C
    Si S est vide :
        Ajouter cl à S
    Sinon :
        Pour tout les superclients (scl dans S):
            Si d(scl, cl) < r :
                Ajouter l'id de cl dans les enfants de scl et augmenter la demande
        Si aucun parent trouvé :
            Ajouter cl à S



Comment savoir si un ensemble de super client est cohérent / raisonnable ?
________________________________________________________________________________________________________________________
L'écart entre le coût avant approximation et le coût après est donné inférieur ou égale à l'erreur suivante :
    err <= r d_cl_c ou d_cl_c est la demande du client que l'on souhaite rajouter
Ainsi, l'erreur est proportionelle au rayon (ce qui au demeurant était logique) mais également proportionelle à la
demande du client à rajouter !!
"""

# Imports
import random
import numpy as np
import json_reader as jr
import matplotlib.pyplot as plt
import PL as pl
import os as os
from datetime import datetime
import cout as co

# Données

file = "KIRO-large"

file_name = file + ".json"
file_name_path = "instances/" + file_name
file_name_sol = "sol-" + file_name
name_dir = "solution/" + file + "___Super_client___" + str(datetime.now().date()) + "___" + str(
    datetime.now().hour) + "_" + str(datetime.now().minute) + "_" + str(datetime.now().second)
file_name_sol_path = name_dir + "/" + file_name_sol

parameters, clients, sites, siteSiteDistances, siteClientDistances = jr.read_data(file_name_path)
nb_client = len(clients)
nb_site = len(sites)
print("nb_clients = ", nb_client)
print("nb_sites = ", nb_site)


# Super Client

class Super_client:
    id: int
    coordinates: list
    demand: int
    children: list
    parent: int

    def __init__(self, _id, _coord, _demand):
        self.id = _id
        self.coordinates = _coord
        self.demand = _demand
        self.parent = 0
        self.children = []


# Glouton

def norm(coord1, coord2):
    value = (coord1[0] - coord2[0]) * (coord1[0] - coord2[0]) + (coord1[1] - coord2[1]) * (coord1[1] - coord2[1])
    value = np.sqrt(value)
    return value


def glouton_super_client(r: float, d: float, liste_client: list, parameters, info=False):
    if info:
        print("#############################################")
        print("#  Glouton Super clients")
        print("#  Rayon r : " + str(r))
    set_super_client = []
    set_client = liste_client.copy()
    maximum_demand = 0
    for client in set_client:
        if client["demand"] >= maximum_demand:
            maximum_demand = client["demand"]
    if info:
        print("#  Demande maximum : " + str(maximum_demand))
        print("#  Marge d'erreur : " + str(d))
        print("# \n#  Calcul en cours ...\n#")
    while len(set_client) != 0:
        tirage = random.randint(0, len(set_client) - 1)
        client_tire = set_client[tirage]
        sortie_boucle = False
        del set_client[tirage]
        if len(set_super_client) == 0:
            set_super_client.append(
                Super_client(client_tire["id"], client_tire["coordinates"], client_tire["demand"]))
        else:
            for super_client in set_super_client:
                if (norm(super_client.coordinates, client_tire["coordinates"]) <= r and not sortie_boucle and
                        client_tire["demand"] <= d * maximum_demand and super_client.demand < parameters["capacities"][
                            "productionCenter"]):
                    super_client.children.append(tirage)
                    super_client.demand += client_tire["demand"]
                    sortie_boucle = True
            if (not sortie_boucle):
                set_super_client.append(
                    Super_client(client_tire["id"], client_tire["coordinates"], client_tire["demand"]))
    if info:
        print("#  Nombre de clients initial : " + str(len(liste_client)))
        print("#  Nombre de clients final : " + str(len(set_super_client)))
        print("#############################################")
    return set_super_client


# Affichage

def show_client_site(name):
    x1, x2 = [], []
    y1, y2 = [], []
    size = []
    for id_client in range(nb_client):
        x1.append(clients[id_client]["coordinates"][0])
        y1.append(clients[id_client]["coordinates"][1])
        size.append(clients[id_client]["demand"] / 1000)
    for id_site in range(nb_site):
        x2.append(sites[id_site]["coordinates"][0])
        y2.append(sites[id_site]["coordinates"][1])

    plt.scatter(x1, y1, s=size)
    plt.scatter(x2, y2)

    plt.title('Répartition des clients et des sites')
    plt.xlabel('x')
    plt.ylabel('y')

    plt.savefig(name + '/Repartition_normale.png')
    plt.show()


def show_super_client(set_super, sites, name):
    x1, x2 = [], []
    y1, y2 = [], []
    size = []
    for el in set_super:
        x1.append(el.coordinates[0])
        y1.append(el.coordinates[1])
        size.append(el.demand / 1000)
    for id_site in range(nb_site):
        x2.append(sites[id_site]["coordinates"][0])
        y2.append(sites[id_site]["coordinates"][1])

    for el in set_super:
        if el.parent != 0:
            plt.plot([el.coordinates[0], sites[el.parent - 1]["coordinates"][0]],
                     [el.coordinates[1], sites[el.parent - 1]["coordinates"][1]], color='black')
    plt.scatter(x1, y1, s=size, c="red")
    plt.scatter(x2, y2, c="orange")

    plt.title('Répartition des clients et des sites')
    plt.xlabel('x')
    plt.ylabel('y')

    plt.savefig(name + '/Repartition_super.png')
    plt.show()


# Création nouveau client

def new_json(set_super: list, para, clie, sit, siteSite, siteClie, file):
    rep = {"parameters": para, "clients": [], "sites": sit, "siteSiteDistances": siteSite, "siteClientDistances": []}
    for client in set_super:
        rep["clients"].append({"id": client.id, "demand": client.demand, "coordinates": client.coordinates})
    for i in range(len(sit)):
        site_coord = []
        for client in set_super:
            site_coord.append(siteClie[i][client.id - 1])
        rep["siteClientDistances"].append(site_coord)
    jr.write_data(file_name=file, data_dictionary=rep)


def create_solution(parameters, client, sites, set_super):
    nb_site = len(sites)
    nb_client = len(client)
    x_production = [0 for i in range(nb_site)]
    x_distribution = [0 for i in range(nb_site)]
    x_automatisation = [0 for i in range(nb_site)]
    x_parent = [[0 for i in range(nb_site)] for j in range(nb_site)]
    x_client = [[0 for i in range(nb_site)] for j in range(nb_client)]
    for client in set_super:
        x_distribution[client.parent - 1] = 1
        x_client[client.id - 1][client.parent - 1] = 1
    for i in range(nb_site):
        if x_distribution[i] == 0:
            x_production[i] = 1
    for client in set_super:
        for child in client.children:
            x_client[child - 1][client.parent - 1] = 1
    return [x_production, x_distribution, x_automatisation, x_parent, x_client]


def check_constraint(X, nb_site, nb_client):
    check = True
    # Au plus un batiment par site
    for id_site in range(nb_site):
        if not (X[0][id_site] + X[1][id_site] <= 1):
            print("Il y a plus d'un batiment sur un des sites " + str(id_site + 1))
            check = False
    # Automatisation seulement sur les centres de production
    for id_site in range(nb_site):
        if not (X[2][id_site] <= X[0][id_site]):
            print("mauvaise automatisation " + str(id_site + 1))
            check = False
    # Parents des centres de distribution (~unicité)
    for id_site in range(nb_site):
        if not (np.sum(X[3][id_site]) == X[1][id_site]):
            print("Parents non unique (centres de distribution) " + str(id_site + 1))
            check = False
    # Parents (validité du parent)
    for id_site in range(nb_site):
        for id_parent in range(nb_site):
            if not (X[3][id_site][id_parent] <= X[0][id_parent]):
                print("Parents incompatibles (centres de distribution) --> site : " + str(
                    id_site + 1) + " --> parent : " + str(id_parent + 1))
                check = False
    # Clients (unicité)
    for id_client in range(nb_client):
        if not (np.sum(X[4][id_client]) == 1):
            print("Parents non unique (clients) " + str(id_client + 1))
            check = False
    # Clients (validité du parent)
    for id_client in range(nb_client):
        for id_parent in range(nb_site):
            if not (X[4][id_client][id_parent] <= X[0][id_parent] + X[1][id_parent]):
                print("Parents incompatibles (clients) --> client : " + str(id_client + 1) + " --> parent : " + str(
                    id_parent + 1))
                check = False
    return check


# Ajuster la solution à tous les clients

if __name__ == "__main__":
    os.makedirs(name_dir, exist_ok=True)
    set_super_client = glouton_super_client(0.5, 0.5, clients, parameters, True)
    show_client_site(name_dir)
    show_super_client(set_super_client, sites, name_dir)
    # X = create_solution(parameters,clients,sites,set_super_client)
    # check_constraint(X,len(sites), len(clients))
    # X = pl.solution_pl(parameters,clients,sites,siteSiteDistances,siteClientDistances)
    # jr.write_data(jr.encode_x(X),file_name_sol_path)
    # print(co.total_cost(X,parameters,clients,sites,siteSiteDistances,siteClientDistances)/10000)
