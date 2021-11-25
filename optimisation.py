def heuristique1():
    min = 100000000000000000
    j_choice_to_construct = 0
    for j in range(nb_site):
        # if la distance moyenne d'un site est plus petite que la moyenne on prend ce site
        dist_moy = np.abs(np.mean(siteClientDistances[:, j]))
        if (dist_moy < min):
            min = dist_moy
            j_choice_to_construct = j
    return 0