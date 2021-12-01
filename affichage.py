
def print_client(x,k,nb_site):
    client_string = "["
    for i in range(nb_site):
        client_string += str(x[k][i].value()) + "  "
    client_string += "]"
    print(client_string)

def print_site(x,nb_site):
    site_string = "["
    for i in range(nb_site):
        site_string += str(x[i].value()) + "  "
    site_string += "]"
    print(site_string)

def result(x_c, x_d, x_a, x_p, x_cl,nb_site,nb_client):
    print(
        "ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")
    print("RESULTATS \n")
    print("centres de production")
    print_site(x_c,nb_site)
    print("centres de distribution")
    print_site(x_d,nb_site)
    print("automatisation")
    print_site(x_a,nb_site)
    print("parents")
    for i in range(nb_site):
        print_client(x_p,i,nb_site)
    print("clients")
    for i in range(nb_client):
        print_client(x_cl, i,nb_site)
    print(
        "ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")