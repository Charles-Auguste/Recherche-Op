# Imports
import random
import numpy as np
import json_reader as jr
import matplotlib.pyplot as plt
import PL as pl
import os as os
import Heuristique_SuperClient as hsc
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
    nb_cluster = 3
else:
    nb_cluster = 3
print("nb_clusters = ", nb_cluster)
max_nb_site = 20
max_site_need_super_client = 13

add_super_client = []
use_super_client = False


def get_liste_coord(liste_client: list):
    liste_client_coord = []
    for client in liste_client:
        liste_client_coord.append(client["coordinates"])
    return liste_client_coord


# Renvoie le cluster auquel appartient les clients puis les sites
# prediction[:nb_client] puis prediction[nb_client:]
def clustering_on_random_centers(number_of_cluster: int, liste_client_coord: list, liste_site_coord: list):
    list_all_coord = liste_client_coord + liste_site_coord
    id = [i for i in range(len(liste_site_coord))]
    centers_id = np.random.choice(id, nb_cluster, replace=False)
    centers = []
    for i in range(len(centers_id)):
        centers.append(liste_site_coord[centers_id[i]])
    kmeans = cluster.MiniBatchKMeans(n_clusters=nb_cluster, init=np.asarray(centers))
    kmeans.fit(list_all_coord)
    predictions = kmeans.labels_.astype(int) + number_of_cluster

    predictions_site = predictions[nb_client:]
    count = np.unique(predictions_site, return_counts=True)[1]
    for i in range(len(np.unique(predictions_site))):
        if count[i] > max_nb_site:
            return clustering_on_random_centers(number_of_cluster, liste_client_coord, liste_site_coord)

    return predictions


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
            sub_prediction = sub_clustering(3, get_liste_coord(sub_list_client), get_liste_coord(sub_list_site),
                                            1 + len(np.unique(predictions)))
            for i in range(len(slice_index_client)):
                predictions[slice_index_client[i]] = sub_prediction[i]
            for i in range(len(slice_index_site)):
                predictions[nb_client + slice_index_site[i]] = sub_prediction[i + len(slice_index_client)]

    predictions_site = predictions[nb_client:]
    count = np.unique(predictions_site, return_counts=True)[1]
    max_rayon = 2
    for i in range(len(np.unique(predictions_site))):
        if count[i] > max_site_need_super_client:
            add_super_client.append(
                (count[i] - max_site_need_super_client) / (max_nb_site - max_site_need_super_client))
        else:
            add_super_client.append(0)

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


def re_allocation_a_la_main(predictions):
    cluster_gauche = predictions[nb_client + 40 - 1]
    rattache_gauche = predictions[nb_client + 50 - 1]

    mix_haut = predictions[nb_client + 35 - 1]
    mix_bas = predictions[nb_client + 31 - 1]
    for i in range(nb_site):
        if(predictions[nb_client+i] == mix_haut or prediction[nb_client+i] == rattache_gauche):
            predictions[nb_client + i] = mix_bas
        #if (predictions[nb_client + i] == rattache_gauche):
        #    predictions[nb_client + i] = cluster_gauche
    #predictions[nb_client + 47 - 1] = mix_bas
    #predictions[nb_client + 25 - 1] = mix_bas
    #predictions[nb_client + 38 - 1] = predictions[nb_client + 42 - 1]
    re_allocation(predictions)
    print(mix_bas)
    uniq = np.unique(predictions[nb_client:])
    pred_copy = uniq.copy()
    print(pred_copy.tolist())
    new_subproblem = pred_copy.tolist().index(mix_bas)
    print(new_subproblem)
    return predictions, new_subproblem

def solution_heuristique2(X, new_sub_prob, parameters, list_sub_client, list_sub_site, list_sub_siteSiteDistance,
                         list_sub_siteClientDistance,
                         list_index_clients, list_index_sites, problem1=None, problem2=None):
    if (problem1 == None):
        subX = [i for i in range(len(list_sub_client))]
        # add_super_client = [0 for i in  range(len(list_sub_client))]
        print(add_super_client)
        set_super_client = None
        for subproblem in range(len(list_sub_clients)):
            print("============")
            print("subproblem numero: ", subproblem)
            print("nb_site: ", len(list_sub_site[subproblem]))
            if (subproblem == new_sub_prob):
                subX[subproblem] = pl.solution_pl(parameters, list_sub_client[subproblem], list_sub_site[subproblem],
                                       list_sub_siteSiteDistance[subproblem],
                                       list_sub_siteClientDistance[subproblem], set_super_client)
            print("============")
        return solution_reconstruction2(subX, list_index_clients, list_index_sites, new_sub_prob,X)


def solution_heuristique(parameters, list_sub_client, list_sub_site, list_sub_siteSiteDistance,
                         list_sub_siteClientDistance,
                         list_index_clients, list_index_sites, problem1=None, problem2=None):
    if (problem1 == None):
        subX = [i for i in range(len(list_sub_clients))]
        # add_super_client = [0 for i in  range(len(list_sub_client))]
        print(add_super_client)
        set_super_client = None
        for subproblem in range(len(list_sub_clients)):
            print("============")
            print("subproblem numero: ", subproblem)
            print("============")
            if (use_super_client):
                set_super_client = hsc.glouton_super_client(add_super_client[subproblem], 0.3,
                                                            list_sub_client[subproblem].tolist(), parameters, True)
                hsc.link_distribution(set_super_client, list_sub_site[subproblem].tolist(), 1)
            subX[subproblem] = pl.solution_pl(parameters, list_sub_client[subproblem], list_sub_site[subproblem],
                                       list_sub_siteSiteDistance[subproblem],
                                       list_sub_siteClientDistance[subproblem], set_super_client)
        return solution_reconstruction(subX, list_index_clients, list_index_sites)
    else:
        subX = []
        # add_super_client = [0 for i in  range(len(list_sub_client))]
        print(add_super_client)
        set_super_client = None
        problems = [problem1, problem2]
        for subproblem in problems:
            if (use_super_client):
                set_super_client = hsc.glouton_super_client(add_super_client[subproblem], 0.3,
                                                            list_sub_client[subproblem].tolist(), parameters, True)
                hsc.link_distribution(set_super_client, list_sub_site[subproblem].tolist(), 1)
            subX.append(pl.solution_pl(parameters, list_sub_client[subproblem], list_sub_site[subproblem],
                                       list_sub_siteSiteDistance[subproblem],
                                       list_sub_siteClientDistance[subproblem], set_super_client))
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




def solution_reconstruction2(subX, list_id_client, list_id_site, new_subprob, X):
    x_production = X[0]
    x_distribution = X[1]
    x_auto = X[2]
    x_parent = X[3]
    x_client = X[4]
    for subproblem in range(len(subX)):
        if subproblem == new_subprob:
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


def fix_var(X, nb_site_non_fix, nb_client_non_fix, predictions_site):
    tirage_liste = [i for i in range(nb_site)]
    index_liste = np.random.choice(tirage_liste, nb_site - nb_site_non_fix, replace=False)

    foo = False
    while(foo==False):
        index_liste = []
        tirage_liste_2 = [i for i in range(nb_site)]
        tirage2 = np.random.choice(tirage_liste_2)
        numpySi = np.asarray(siteSiteDistances)
        numpyS = numpySi[:, tirage2]

        k = nb_site_non_fix
        idx = np.argpartition(numpyS, k)
        index_liste_non_fix = idx[:k]
        print(numpyS[index_liste_non_fix])
        n_predictions_site = np.asarray(predictions_site)
        predictions_site_non_fixe = n_predictions_site[index_liste_non_fix]
        count = np.unique(predictions_site_non_fixe, return_counts=True)[1]
        print(count)
        print(predictions_site_non_fixe)
        if(len(count) > 1):
            foo = True
        for i in range(nb_site):
            if i not in index_liste_non_fix:
                index_liste.append(i)

    fix_c = dict()
    fix_d = dict()
    fix_a = dict()
    fix_p = dict()

    for i in range(len(index_liste)):
        fix_c[index_liste[i]] = X[0][index_liste[i]]
        fix_d[index_liste[i]] = X[1][index_liste[i]]
        fix_a[index_liste[i]] = X[2][index_liste[i]]
    return fix_c, fix_d, fix_a


if __name__ == "__main__":
    os.makedirs(name_dir, exist_ok=True)
    best_solution_known_file = "best_solution/" + "depart3abc.json"
    try:
        X = jr.decode(best_solution_known_file, nb_site)
        print("solution trouvee")
    except:
        print("solution pas trouvee")
        list_client_coord = get_liste_coord(clients)
        list_site_coord = get_liste_coord(sites)

        prediction = clustering(nb_cluster, list_client_coord, list_site_coord)
        prediction = re_allocation(prediction)
        prediction,subprob = re_allocation_a_la_main(prediction)
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
'''
    print("Coût de la solution optimale : ")
    print(int(co.total_cost(X, parameters, clients, sites, siteSiteDistances, siteClientDistances) / 10000))
    cout_before = int(co.total_cost(X, parameters, clients, sites, siteSiteDistances, siteClientDistances) / 10000)

    list_client_coord = get_liste_coord(clients)
    list_site_coord = get_liste_coord(sites)

    prediction = clustering(nb_cluster, list_client_coord, list_site_coord)
    prediction = re_allocation(prediction)
    prediction, new_subprob = re_allocation_a_la_main(prediction)

    # show_client_site_clustered(name_dir, prediction)

    list_sub_clients, list_sub_sites, list_sub_siteSiteDistances, list_sub_siteClientDistances, list_index_client, list_index_site = get_sub_problem(
        prediction)
    # show_client_site(name_dir)
    # show_client_site_clustered(name_dir, prediction)
    
    print_sub_problem_stat(prediction, list_sub_clients, list_sub_sites)
    # show_super_client(set_super_client,name_dir)
    X = solution_heuristique2(X, new_subprob, parameters, list_sub_clients, list_sub_sites, list_sub_siteSiteDistances,
                             list_sub_siteClientDistances, list_index_client, list_index_site,)

    jr.write_data(jr.encode_x(X), file_name_sol_path)
    print(int(co.total_cost(X, parameters, clients, sites, siteSiteDistances, siteClientDistances) / 10000))
'''

'''
    for i in range(10):
        fix_c, fix_d, fix_a = fix_var(X, 4, 0, prediction[nb_client:])
        #set_super_client = glouton_super_client(2, 0.5, clients, parameters, True)
        #link_distribution(set_super_client, sites, 1)
        new_X = pl.solution_pl(parameters, clients, sites, siteSiteDistances, siteClientDistances, fix_c=fix_c, fix_d=fix_d,
                               fix_a=fix_a)
        print("Coût de la solution optimale : ")
        print(int(co.total_cost(new_X, parameters, clients, sites, siteSiteDistances, siteClientDistances) / 10000))
        cout_after = int(co.total_cost(new_X, parameters, clients, sites, siteSiteDistances, siteClientDistances) / 10000)

        print(cout_before-cout_after)

        if(cout_before-cout_after>0):
            X = new_X
        jr.write_data(jr.encode_x(new_X), file_name_sol_path+str(i))
    '''