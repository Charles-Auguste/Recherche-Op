# Imports
import random
import numpy as np
import json_reader as jr
import matplotlib.pyplot as plt
import PL as pl
import os as os
from datetime import datetime
import cout as co

# Imports de clustering
from sklearn import cluster, datasets, mixture
from sklearn.neighbors import kneighbors_graph
from sklearn.preprocessing import StandardScaler
from itertools import cycle, islice

# Données

file = "KIRO-large"

file_name = file + ".json"
file_name_path = "instances/" + file_name
file_name_sol = "sol-" + file_name
name_dir = "solution/" + file + "___" + str(datetime.now().date()) + "___" + str(datetime.now().hour) + "_" + str(
    datetime.now().minute) + "_" + str(datetime.now().second)
file_name_sol_path = name_dir + "/" + file_name_sol

parameters, clients, sites, siteSiteDistances, siteClientDistances = jr.read_data(file_name_path)
nb_client = len(clients)
nb_site = len(sites)
print("nb_clients = ", nb_client)
print("nb_sites = ", nb_site)

# Le nombre de cluster dépend de l'instance
if file == "KIRO-large":
    nb_cluster = 6  # idee max 10 sites par cluster
elif file == "KIRO-medium":
    nb_cluster = 4
else:
    nb_cluster = 3
print("nb_clusters = ", nb_cluster)
max_nb_site = 11


# Super Client

class Super_client:
    id: int
    coordinates: list
    demand: int
    children: list

    def __init__(self, _id, _coord, _demand):
        self.id = _id
        self.coordinates = _coord
        self.demand = _demand
        self.children = []


# Glouton

def norme(coord1, coord2):
    valeur = (coord1[0] - coord2[0]) * (coord1[0] - coord2[0]) + (coord1[1] - coord2[1]) * (coord1[1] - coord2[1])
    valeur = np.sqrt(valeur)
    return valeur


def get_liste_coord(liste_client: list):
    liste_client_coord = []
    for client in liste_client:
        liste_client_coord.append(client["coordinates"])
    return liste_client_coord


# Renvoie le cluster auquel appartient les clients puis les sites
# prediction[:nb_client] puis prediction[nb_client:]
def clustering(number_of_cluster: int, liste_client_coord: list, liste_site_coord: list):
    list_all_coord = liste_client_coord + liste_site_coord
    spectral = cluster.SpectralClustering(
        n_clusters=number_of_cluster,
        eigen_solver="arpack",
        affinity="nearest_neighbors",
    )
    spectral.fit(list_all_coord)
    predictions = spectral.labels_.astype(int)
    predictions_client = predictions[:nb_client]
    predictions_site = predictions[nb_client:]
    count = np.unique(predictions_site, return_counts=True)[1]
    for label in np.unique(predictions_site):
        if count[label] > max_nb_site:
            slice_index_client = []
            slice_index_site = []
            for i in range(len(predictions_client)):
                if predictions[i] == label:
                    slice_index_client.append(i)
            for i in range(len(predictions_site)):
                if predictions[nb_client + i] == label:
                    slice_index_site.append(i)
            numpy_clients = np.asarray(clients)
            numpy_sites = np.asarray(sites)
            sub_list_client = numpy_clients[slice_index_client]
            sub_list_site = numpy_sites[slice_index_site]
            sub_prediction = sub_clustering(4, get_liste_coord(sub_list_client), get_liste_coord(sub_list_site),
                                            1 + len(np.unique(predictions)))
            for i in range(len(slice_index_client)):
                predictions[slice_index_client[i]] = sub_prediction[i]
            for i in range(len(slice_index_site)):
                predictions[nb_client + slice_index_site[i]] = sub_prediction[i + len(slice_index_client)]
    return predictions


# On affine la clusterisation
def sub_clustering(number_of_sub_cluster: int, sub_liste_client_coord: list, sub_liste_site_coord: list,
                   number_of_cluster: int):
    list_all_coord = sub_liste_client_coord + sub_liste_site_coord
    kmeans = cluster.MiniBatchKMeans(n_clusters=number_of_sub_cluster)
    kmeans.fit(list_all_coord)
    sub_predictions = kmeans.labels_.astype(int) + number_of_cluster
    # print(np.unique(sub_predictions))
    return sub_predictions


def show_client_site(name):
    plt.figure()
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


def show_client_site_clustered(name, predictions: list):
    plt.figure()
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

    predictions_client = predictions[:nb_client]
    plt.scatter(x1, y1, c=predictions_client, s=size)
    plt.scatter(x2, y2, c='#d62728')

    plt.title('Répartition des clients et des sites')
    plt.xlabel('x')
    plt.ylabel('y')

    plt.savefig(name + '/Repartition_cluster.png')
    plt.show()


def print_sub_problem_stat(predictions, list_sub_client, list_sub_site):
    for label in range(len(np.unique(predictions))):
        print("taille du sous problème " + str(label) + ":")
        print("nb_sub_client:", len(list_sub_client[label]))
        print("nb_sub_site", len(list_sub_site[label]))
        print(" ")


def get_sub_problem(predictions: list):
    # numpy pour pouvoir slicer sur des tuples
    numpy_clients = np.asarray(clients)
    numpy_sites = np.asarray(sites)
    numpy_siteSiteDistances = np.asarray(siteSiteDistances)
    numpy_siteClientDistances = np.asarray(siteClientDistances)
    list_sub_client = []
    list_sub_site = []
    list_sub_siteSiteDistance = []
    list_sub_siteClientDistance = []
    predictions_client = predictions[:nb_client]
    predictions_site = predictions[nb_client:]
    list_slice_index_client = []
    list_slice_index_site = []
    for label in np.unique(predictions):
        slice_index_client = []
        slice_index_site = []
        for i in range(len(predictions_client)):
            if predictions[i] == label:
                slice_index_client.append(i)
        for i in range(len(predictions_site)):
            if predictions[nb_client + i] == label:
                slice_index_site.append(i)
        list_sub_client.append(numpy_clients[slice_index_client])
        list_sub_site.append(numpy_sites[slice_index_site])
        list_sub_siteSiteDistance.append(numpy_siteSiteDistances[slice_index_site, :][:, slice_index_site])
        list_sub_siteClientDistance.append(numpy_siteClientDistances[slice_index_site, :][:, slice_index_client])
        # sauvegarde des indices des sous problèmes pour reconstruire la solution finale
        list_slice_index_client.append(slice_index_client)
        list_slice_index_site.append(slice_index_site)
    return list_sub_client, list_sub_site, list_sub_siteSiteDistance, list_sub_siteClientDistance, list_slice_index_client, list_slice_index_site


def re_allocation(predictions):
    numpy_siteClientDistances = np.asarray(siteClientDistances)
    for i in range(nb_client):
        j_min = np.argmin(numpy_siteClientDistances[:, i])
        predictions[i] = predictions[nb_client + j_min]
    return predictions


def solution_heuristique(parameters, list_sub_client, list_sub_site, list_sub_siteSiteDistance,
                         list_sub_siteClientDistance,
                         list_index_clients, list_index_sites):
    subX = []
    for subproblem in range(len(list_sub_clients)):
        subX.append(pl.solution_pl(parameters, list_sub_client[subproblem], list_sub_site[subproblem],
                                   list_sub_siteSiteDistance[subproblem],
                                   list_sub_siteClientDistance[subproblem]))
    return solution_reconstruction(subX, list_index_clients, list_index_sites)


def solution_reconstruction(subX, list_id_client, list_id_site):
    x_production = [0 for i in range(nb_site)]
    x_distribution = [0 for i in range(nb_site)]
    x_auto = [0 for i in range(nb_site)]
    x_parent = [[0 for i in range(nb_site)] for j in range(nb_site)]
    x_client = [[0 for i in range(nb_site)] for j in range(nb_client)]
    for subproblem in range(len(subX)):
        for site in range(len(subX[subproblem][0])):
            x_production[list_id_site[subproblem][site]] = subX[subproblem][0][site]
            x_distribution[list_id_site[subproblem][site]] = subX[subproblem][1][site]
            x_auto[list_id_site[subproblem][site]] = subX[subproblem][2][site]
        for site1 in range(len(subX[subproblem][0])):
            for site2 in range(len(subX[subproblem][0])):
                x_parent[list_id_site[subproblem][site1]][list_id_site[subproblem][site2]] = \
                    subX[subproblem][3][site1][site2]
        for site in range(len(subX[subproblem][0])):
            # je suis pas sur du 0
            # print("site", len(subX[subproblem][0]))
            # print("client", len(subX[subproblem][4]))
            for client in range(len(subX[subproblem][4])):
                x_client[list_id_client[subproblem][client]][list_id_site[subproblem][site]] = \
                    subX[subproblem][4][client][site]
    return [x_production, x_distribution, x_auto, x_parent, x_client]


if __name__ == "__main__":
    os.makedirs(name_dir, exist_ok=True)
    list_client_coord = get_liste_coord(clients)
    list_site_coord = get_liste_coord(sites)
    prediction = clustering(nb_cluster, list_client_coord, list_site_coord)
    prediction = re_allocation(prediction)
    list_sub_clients, list_sub_sites, list_sub_siteSiteDistances, list_sub_siteClientDistances, list_index_client, list_index_site = get_sub_problem(
        prediction)
    # show_client_site(name_dir)
    show_client_site_clustered(name_dir, prediction)

    print_sub_problem_stat(prediction, list_sub_clients, list_sub_sites)
    # show_super_client(set_super_client,name_dir)
    X = solution_heuristique(parameters, list_sub_clients, list_sub_sites, list_sub_siteSiteDistances,
                             list_sub_siteClientDistances, list_index_client, list_index_site)
    jr.write_data(jr.encode_x(X), file_name_sol_path)

    print("Coût de la solution optimale : ")
    print(int(co.total_cost(X, parameters, clients, sites, siteSiteDistances, siteClientDistances) / 10000))
