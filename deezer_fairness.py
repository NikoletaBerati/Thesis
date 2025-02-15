import networkx as nx
import csv
import pandas as pd

def detect_louvain_communities(graph):
    partition = nx.community.louvain_communities(graph)
    print("\nLOUVAIN ALGORITHM\n")
    return partition


def detect_label_communities(graph):
    partition = nx.community.label_propagation_communities(graph)
    partition = list(partition)
    print("\nLABEL PROPAGATION ALGORITHM\n")
    return partition

def detect_fluid_communities(graph):
    partition = nx.community.asyn_fluidc(graph, k=20)
    partition = list(partition)
    print("\nFLUID COMMUNITIES ALGORITHM\n")
    return partition 
    

def get_dataset():
    filename = "deezer_europe/deezer_europe_edges.csv"
    dataset = nx.read_edgelist(filename, delimiter=',', nodetype=int)
    con_component = max(nx.connected_components(dataset), key=len)
    deezer_largest_component = dataset.subgraph(con_component)
    dataset = deezer_largest_component
    return dataset


def load_attributes():
    attributes_file = pd.read_csv("deezer_europe/deezer_europe_target.csv")
    id = attributes_file["id"]
    gender = attributes_file["target"]
    dict_of_attributes = dict(zip(id, gender))
    return dict_of_attributes


def count_red_and_blue_nodes():
    red = 0
    blue = 0
    # count total number of each attribute
    with open("deezer_europe/deezer_europe_target.csv", "r") as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader) # skip the header row
        for row in csv_reader:
            if row[1] == '1':
                blue += 1
            else:
                red += 1
    print("Total number of red nodes:", red)
    print("Total number of blue nodes: ", blue)
    return red, blue


def calculate_red_percentage(total_red_nodes, total_nodes):
    f = total_red / number_of_nodes
    print(f"Overall percentage of red nodes is: f = {f} \n")
    return f


def count_attributes_communities(communities):
    community_blue = {}
    community_red = {}
    for community in communities:
        red_counter = 0
        blue_counter = 0
        for node in community: 
            if dict_of_attributes[node] == 0: # red
                red_counter += 1
            elif dict_of_attributes[node] == 1: # blue
                blue_counter += 1
        community_red[str(community)] = red_counter
        community_blue[str(community)] = blue_counter
    return community_blue, community_red




def count_community_fairness(communities):
    community_fairness = {}
    i = 0
    fairness_balance = 0
    mean_fairness = 0
    mean_fairness_of_communities = 0

    for community, blue_counter in community_blue.items():
        red_counter = len(communities[i]) - blue_counter
        fairness_balance = (red_counter / len(communities[i])) - f
        community_fairness[community] = fairness_balance
        mean_fairness = mean_fairness + fairness_balance
        i += 1
    mean_fairness_of_communities = mean_fairness/len(communities)
    return mean_fairness_of_communities, community_fairness





def return_mean_fairness(fairness_dictionary):
    total_fairness = 0
    mean_fairness = 0
    for community, fairness in fairness_dictionary.items():
        total_fairness += fairness
    mean_fairness = total_fairness / len(communities)
    return mean_fairness


# returns dictionary with communities and degree of each node
def get_communities_degrees(dataset, communities):
    communities_degrees = {}
    for index, community in enumerate(communities):
        community_degrees = {}
        community_subgraph = dataset.subgraph(community)
        for node in community_subgraph.nodes():
            community_degrees[node] = community_subgraph.degree(node)
        communities_degrees[f"Community_{index}"] = community_degrees
    return communities_degrees

# returns dictionary with nodes from every community that have low degrees
def get_low_communities_degrees(communities_degrees):
    low_degree_nodes = {}

    for community, node_degrees in communities_degrees.items():
        community_size = len(node_degrees) # number of nodes in this community
        threshold = community_size * 0.3
        low_degree_nodes[community] = {}
        for node, degree in node_degrees.items():
            if degree < threshold:
                low_degree_nodes[community][node] = degree
    return low_degree_nodes

def get_low_degree_attributes(blue_nodes, red_nodes):
    degrees_of_all_nodes = get_communities_degrees(dataset, communities)
    low_degree_nodes = get_low_communities_degrees(degrees_of_all_nodes)
    blue_nodes_low_degree = []
    red_nodes_low_degree = []
    for community, dict_degrees in low_degree_nodes.items():
        for node, degree in dict_degrees.items():
            if node in blue_nodes:
                blue_nodes_low_degree.append(node)
            if node in red_nodes:
                red_nodes_low_degree.append(node)            
    return blue_nodes_low_degree, red_nodes_low_degree

def split_communities_by_fairness(community_fairness):
    positive_fairness = {}
    negative_fairness = {}
    positive = []
    negative = []
    for community, fairness in community_fairness.items():
        c = community
        if fairness >= 0:
            positive_fairness[community] = fairness
        elif fairness < 0:
            negative_fairness[community] = fairness

    #now i want to sort them in descending and ascending order
    sorted_positive_fairness = dict(sorted(positive_fairness.items(), key=lambda item: item[1], reverse=True))
    sorted_negative_fairness = dict(sorted(negative_fairness.items(), key=lambda item: item[1]))
    
    for community, fairness in sorted_positive_fairness.items():
        c = list(eval(community))
        positive.append(c)
    for community, fairness in sorted_negative_fairness.items():
        c = list(eval(community))
        negative.append(c)
    return positive, negative



def seperate_nodes(community):
    blue_nodes_in_community = []
    red_nodes_in_community = []
    for node in community:
        if dict_of_attributes[node] == 0:
            red_nodes_in_community.append(node)
        else:
            blue_nodes_in_community.append(node)
    return blue_nodes_in_community, red_nodes_in_community


def get_red_and_blue_nodes(communities):
    red_nodes_in_communities = []
    blue_nodes_in_communities = []
    for community in communities:
        for node in community:
            if dict_of_attributes[node] == 0:
                red_nodes_in_communities.append(node)
            else:
                blue_nodes_in_communities.append(node)
    return red_nodes_in_communities, blue_nodes_in_communities


def improve_balance_fairness(communities):
    mean_fairness, fairness_dict = count_community_fairness(communities)
    print("Old mean balance fairness: ", mean_fairness)
    positive, negative = split_communities_by_fairness(fairness_dict)
    communities_copy = [list(community) for community in communities]
    communities_copy = [sorted(sublist) for sublist in communities_copy]
    red_nodes, blue_nodes = get_red_and_blue_nodes(communities_copy)

    for community in negative:
        blue_nodes_in_community, red_nodes_in_community = seperate_nodes(community)
        blue_nodes_low_degree, red_nodes_low_degree = get_low_degree_attributes(blue_nodes_in_community, red_nodes_in_community)
        communities_copy, positive = exchange_nodes(community, positive, blue_nodes_low_degree, communities_copy)

        new_modularity = nx.community.modularity(dataset, communities_copy)
        if (new_modularity <= (2*initial_modularity)/3):
            break

    new_dictionary = {}
    for community in communities_copy:
        new_dictionary[str(community)] = calculate_fairness(community, red_nodes)

    new_mean_fairness = return_mean_fairness(new_dictionary)
    print("New mean balance fairness: ", new_mean_fairness)

    return new_dictionary, communities_copy



def exchange_nodes(community, target_communities, nodes_to_leave, communities):
    community = sorted(community)
    index_community = communities.index(community) # returns position in list of that community
    target_communities = [sorted(sublist) for sublist in target_communities]
    
    for blue_node in nodes_to_leave:
        if (blue_node in community) :
            target_communities = [sorted(sublist) for sublist in target_communities]

            start_community = communities[index_community]
            start_community.remove(blue_node)

            best_target = find_best_community(blue_node, target_communities)

            index_best_target = communities.index(best_target)
            targetCommunity = communities[index_best_target]
            targetCommunity.append(blue_node)
            targetCommunity.sort()

            index = target_communities.index(best_target)
            target_communities[index].append(blue_node)

    return communities, target_communities




def calculate_fairness(community, red_nodes):
    red_nodes_in_community = 0
    for id, node in enumerate(community):
        if node in red_nodes:
            red_nodes_in_community += 1
    fairness = (red_nodes_in_community / len(community)) - f
    return fairness

def calculate_node_degree(node, community):
    community.append(node)
    subgraph = dataset.subgraph(community)
    degree = subgraph.degree(node)
    community.remove(node)
    return degree


def find_best_community(blue_node, target_communities):
    max_degree = 0
    best_community = target_communities[0]
    for community in target_communities:
        degree = calculate_node_degree(blue_node, community)
        if degree > max_degree:
            max_degree = degree
            best_community = community
    best_community = sorted(best_community)
    return best_community




############################################################

####### MODULARITY CALCULATION #######

############################################################


def calculate_modularity(intra_edges, degrees):
    x = intra_edges / number_of_edges
    y = (degrees / (2*number_of_edges)) ** 2
    modularity = x - y
    return modularity


def get_red_and_blue_sum_degrees(subgraph, red_nodes, blue_nodes):
    community_red_sum_degrees = 0
    community_blue_sum_degrees = 0
    community_total_degrees = 0

    red_nodes_set = set(red_nodes)
    blue_nodes_set = set(blue_nodes)

    degrees = dict(subgraph.degree())
    
    community_red_sum_degrees = sum(degrees[node] for node in subgraph.nodes if node in red_nodes_set)
    community_blue_sum_degrees = sum(degrees[node] for node in subgraph.nodes if node in blue_nodes_set)
    community_total_degrees = sum(degrees.values())
    
    return community_red_sum_degrees, community_blue_sum_degrees, community_total_degrees




def intra_with_red_and_blue_endpoints(subgraph, red_nodes, blue_nodes):
    count_red = 0
    count_blue = 0

    red_nodes_set = set(red_nodes)
    blue_nodes_set = set(blue_nodes)

    for u, v in subgraph.edges():
        if u in red_nodes_set or v in red_nodes_set:
            count_red += 1
        if u in blue_nodes_set or v in blue_nodes_set:
            count_blue += 1
    return count_red, count_blue


def calculate_red_modularity(intra_edges, red_degrees_sum, degrees_sum):
    x = intra_edges / number_of_edges
    y = (degrees_sum * red_degrees_sum)/ (2 * number_of_edges)**2
    modularity = x - y
    return modularity

def calculate_blue_modularity(intra_edges, blue_degrees_sum, degrees_sum):
    x = intra_edges / number_of_edges
    y = (degrees_sum * blue_degrees_sum)/ (2 * number_of_edges)**2
    modularity = x - y
    return modularity



def calculate_fairness_modularity(dataset, communities, red_nodes, blue_nodes):
    communities_modularity_fairness = {}

    for community in communities:
        subgraph = dataset.subgraph(community)

        intra_edges_of_community = subgraph.number_of_edges()

        community_red_sum_degrees, community_blue_sum_degrees, community_total_degrees = get_red_and_blue_sum_degrees(subgraph, red_nodes, blue_nodes)
        red_intra_edges, blue_intra_edges = intra_with_red_and_blue_endpoints(subgraph, red_nodes, blue_nodes)

        red_modularity = calculate_red_modularity(red_intra_edges, community_red_sum_degrees, community_total_degrees)

        blue_modularity = calculate_blue_modularity(blue_intra_edges, community_blue_sum_degrees, community_total_degrees)

        modularity = calculate_modularity(intra_edges_of_community, community_total_degrees)

        fairness = calculate_fairness_modularity_of_community(red_modularity, blue_modularity, modularity)

        communities_modularity_fairness[str(community)] = fairness
    return communities_modularity_fairness


############# CALCULATION OF MODULARITY FAIRNESS ON A PARTICULAR COMMUNITY ##############

def calculate_fairness_modularity_of_community(red_modularity, blue_modularity, modularity):
    if (modularity != 0):
        fairness = (red_modularity - blue_modularity) / abs(modularity)
    else:
        fairness = 0
    return fairness





def improve_modularity_fairness(communities) :
    red_nodes, blue_nodes = get_red_and_blue_nodes(communities)
    fairness_modularity = calculate_fairness_modularity(dataset, communities, red_nodes, blue_nodes)
    mean_modularity_fairness = return_mean_fairness(fairness_modularity)
    print("Old mean modularity fairness: ", mean_modularity_fairness)

    positive, negative = split_communities_by_fairness(fairness_modularity)
    communities_copy = [list(community) for community in communities]
    communities_copy = [sorted(sublist) for sublist in communities_copy]


    for community in negative:
        blue_nodes_in_community, red_nodes_in_community = seperate_nodes(community)
        blue_nodes_low_degree, red_nodes_low_degree = get_low_degree_attributes(blue_nodes_in_community, red_nodes_in_community)
        communities_copy, positive = exchange_nodes_for_modularity(community, positive, blue_nodes_low_degree, communities_copy,red_nodes,blue_nodes)

        new_modularity = nx.community.modularity(dataset, communities_copy)
        if (new_modularity <= (2*initial_modularity)/3):
            break

    new_modularity = calculate_fairness_modularity(dataset, communities_copy, red_nodes, blue_nodes)
    mean_modularity = return_mean_fairness(new_modularity)
    print("New mean modularity fairness: ", mean_modularity)
    return mean_modularity, communities_copy


def exchange_nodes_for_modularity(community, target_communities, nodes_to_leave, communities,red_nodes,blue_nodes) :
    community = sorted(community)
    index_community = communities.index(community) # returns position in list of that community
    target_communities = [sorted(sublist) for sublist in target_communities]

    for node in nodes_to_leave:
        if (node in community) :
            start_community = communities[index_community]
            start_community.remove(node)

            best_target = find_best_modularity(node, target_communities,red_nodes,blue_nodes)
     
            index_best_target = communities.index(best_target)
            target_community = communities[index_best_target]
            target_community.append(node)
            target_community.sort()

            target_communities = [sorted(sublist) for sublist in target_communities]

            index = target_communities.index(best_target)
            target_communities[index].append(node)
            
    return communities, target_communities



def find_best_modularity(node, target_communities,red_nodes,blue_nodes):
    best_modularity = 100
    best_target = target_communities[0]

    for target_community in target_communities:
        target_community.append(node)
        subgraph = dataset.subgraph(target_community)
        community_red_sum_degrees, community_blue_sum_degrees, community_total_degrees = get_red_and_blue_sum_degrees(subgraph, red_nodes, blue_nodes)
        red_intra_edges, blue_intra_edges = intra_with_red_and_blue_endpoints(subgraph, red_nodes, blue_nodes)
        red_modularity = calculate_red_modularity(red_intra_edges, community_red_sum_degrees, community_total_degrees)
        blue_modularity = calculate_blue_modularity(blue_intra_edges, community_blue_sum_degrees, community_total_degrees)
        modularity = red_modularity - blue_modularity
        target_community.remove(node)
        if ( modularity >= best_modularity):
            best_modularity = modularity
            best_target = target_community
    best_target = sorted(best_target)
    return best_target




dataset = get_dataset()

number_of_nodes = dataset.number_of_nodes()
number_of_edges = dataset.number_of_edges()


#######################################################
####### CHOOSE THE COMMUNITY DETECTION ALGORITHM ######

communities = detect_louvain_communities(dataset)
#communities = detect_label_communities(dataset)
#communities = detect_fluid_communities(dataset)

#######################################################

print("Communities found:", len(communities))
initial_modularity = nx.community.modularity(dataset, communities)
print("Modularity of communities: ", initial_modularity)

total_red, total_blue = count_red_and_blue_nodes()
dict_of_attributes = load_attributes()
community_blue, community_red = count_attributes_communities(communities)
f = calculate_red_percentage(total_red, number_of_nodes)



#######################################################
###### CHOOSE THE FAIRNESS METRIC TO IMRPOVE

new_dictionary, new_communities = improve_balance_fairness(communities)
#new_dictionary, new_communities = improve_modularity_fairness(communities)

#######################################################



