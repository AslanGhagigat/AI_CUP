# import modules
from src.game import Game
import networkx as nx


# make flag for get global variables in currect time
# bool
get_info = False
get_map = False

# make global variables

# player_id int
my_id = int()

# key: node_id -> str       value: list of neighbors -> str
graph_of_map = dict()
tiny_map = dict()

# networkx graph
graph_of_map_nx = nx.Graph()
tiny_map_nx = nx.Graph()

# strategic nodes list -> str
strategic_nodes = list()

# for choice best strategic node
#
parameters = dict()

# for choice best strategic node
#
normal_parameters = dict()

# key: my node_id -> str    value: how to importent to build up -> int
parametrs_for_build_up = dict()

# key: player_id -> int     value: node have -> int
player_node_count = dict()

# key: node_id -> str       value: score of node_id -> int
strategic_nodes_with_score = dict()

# key: node_id -> str       value: owner player_id (if have't owner -1) -> int
strategic_nodes_with_owner = dict()

# key: node_id -> str       value: player_id (if have't owner -1)  -> int
owners_of_nodes = dict()

# key: node_id -> str       value: troops on this node -> int
troops_on_nodes = dict()

# key: node_id -> str       value: forts on this node -> int
forts_on_nodes = dict()

# key: my node_id -> str    value: troops on this node -> int
my_nodes = dict()

# key: node_id -> str       value: [player_id, troops in node, fort_troops in node] -> int  in turn states
dict_of_owners_with_troops = dict()


# key -> node_id    value -> calculate with length between node and strategic node and possibility of won
node_for_attack_from = dict()


# attack to these node with this arrangement
node_for_attack_to = list()

# first node for attack from
node_id_for_attack = Str()


# Input: dict with int value    Output: dict with str value
def convert_dict_from_int_to_str(dictionary):
    for key in dictionary:
        nodes = []
        for value in dictionary[key]:
            nodes.append(str(value))
        dictionary.update({key: nodes})
    return dictionary


# function for get owners with redesign dictionary and update strategic_nodes_with_owner and owners_of_nodes
def get_new_owners_initializer(game):
    global strategic_nodes_with_owner, troops_on_nodes, my_nodes, my_id, owners_of_nodes, player_node_count
    owners_of_nodes = game.get_owners()
    troops_on_nodes = game.get_number_of_troops()
    p0 = 0
    p1 = 0
    p2 = 0
    for node_id in owners_of_nodes:
        owner_of_node = owners_of_nodes[node_id]

        # update strategic nodes
        if node_id in strategic_nodes_with_owner and owners_of_nodes[node_id] != strategic_nodes_with_owner[node_id]:
            strategic_nodes_with_owner.update(
                {node_id: owners_of_nodes[node_id]})

        # update my nodes
        if owners_of_nodes[node_id] == my_id:
            my_nodes.update({node_id: troops_on_nodes[node_id]})

        # update player node count
        if owner_of_node == 0:
            p0 += 1
        elif owner_of_node == 1:
            p1 += 1
        elif owner_of_node == 2:
            p2 += 1
    player_node_count = {0: p0, 1: p1, 2: p2}


# convert list of list (paths of graph) to dict
def convert_list_to_dict(path, graph):
    for i in range(1, len(path)-1):
        if path[i] not in graph:
            graph.update({path[i]: [path[i-1], path[i+1]]})
        else:
            if path[i-1] not in graph[path[i]]:
                graph[path[i]].append(path[i-1])
            if path[i+1] not in graph[path[i]]:
                graph[path[i]].append(path[i+1])
    if path[0] not in graph:
        graph.update({path[0]: [path[1]]})
    else:
        if path[1] not in graph[path[0]]:
            graph[path[0]].append(path[1])
    if path[-1] not in graph:
        graph.update({path[-1]: [path[-2]]})
    else:
        if path[-2] not in graph[path[-1]]:
            graph[path[-1]].append(path[-2])
    return graph


# make tiny map for play faster with strategic nodes and the shortest path between them
def make_tiny_map(dictionary):
    global tiny_map, strategic_nodes, tiny_map_nx
    G = nx.Graph(dictionary)
    tiny_map_list = []
    for i in strategic_nodes:
        path_between_nodes = []
        for j in range(6):
            if strategic_nodes[j] != i:
                for short_path in nx.all_shortest_paths(G, i, strategic_nodes[j]):
                    if short_path not in tiny_map_list:
                        path_between_nodes.append(short_path)
        length_of_longest_path = len(dictionary)
        for path in path_between_nodes:
            if len(path) < length_of_longest_path:
                shortest_path = []
                length_of_longest_path = len(path)
                shortest_path.append(path)
            elif len(path) == length_of_longest_path and len(shortest_path) < 3:
                shortest_path.append(path)
        for best_path_between_two_strategic_node in shortest_path:
            tiny_map_list.append(best_path_between_two_strategic_node)
        path_between_nodes = []

    for i in tiny_map_list:
        tiny_map = convert_list_to_dict(i, tiny_map)
    tiny_map_nx = nx.Graph(tiny_map)


# set parameters for choice best strategic node
def get_the_best_strategic_nodes():
    global strategic_nodes, strategic_nodes_with_score, tiny_map, tiny_map_nx, parameters

    avr_score = (min(strategic_nodes_with_score.values()) +
                 max(strategic_nodes_with_score.values()))/2

    def calculate_score(score, avr_score):
        return int((score-avr_score)**2 * 100)

    def calculate_distance(distance):
        return int(1000 - distance*50)

    def calculate_normal_n(normal_neighbor):
        return int(normal_neighbor*70)

    def calculate_strategic_n(strategic_neighbor):
        return int(strategic_neighbor*200)

    for node in strategic_nodes:
        normal_neighbor = 0
        strategic_neighbor = 0
        distance = 0
        neighbors = tiny_map[node]
        for neighbor in neighbors:
            if neighbor in strategic_nodes:
                strategic_neighbor += 1
            else:
                normal_neighbor += 1

        for s_node in strategic_nodes:
            distance += nx.shortest_path_length(tiny_map_nx, node, s_node)

        score = strategic_nodes_with_score[node]

        score = calculate_score(score, avr_score)
        s_neighbor = calculate_strategic_n(strategic_neighbor)
        n_neighbor = calculate_normal_n(normal_neighbor)
        distance = calculate_distance(distance)

        parameters.update({node: score + s_neighbor + n_neighbor + distance})
    parameters = dict(
        sorted(parameters.items(), key=lambda x: x[1], reverse=True))


# set parameters for choice best normal node
def get_the_best_normal_nodes():
    global tiny_map, tiny_map_nx, strategic_nodes, normal_parameters
    for node_id in tiny_map:
        distance = 0
        if node_id not in strategic_nodes:
            for s_node in strategic_nodes:
                distance += nx.shortest_path_length(
                    tiny_map_nx, node_id, s_node)
            normal_parameters.update({node_id: distance})
    normal_parameters = dict(
        sorted(normal_parameters.items(), key=lambda x: x[1]))


# list of my nodes with calculate score for troops on its neighbors
# for choice best node for build up
def choice_node_for_build_up():
    global tiny_map_nx, troops_on_nodes, strategic_nodes_with_score, my_nodes, parametrs_for_build_up, graph_of_map_nx
    sum_of_score = sum(strategic_nodes_with_score.values())
    for node_id in my_nodes:
        # neighbors_of_node = [n for n in graph_of_map_nx.neighbors(node_id)]
        neighbors_of_node = [n for n in tiny_map_nx.neighbors(node_id)]
        count_of_neighbors = len(neighbors_of_node)
        neighbors_troop = 0

        # for neighbor in neighbors_of_node:
        #     neighbors_troop += troops_on_nodes[neighbor]

        for neighbor in neighbors_of_node:
            if neighbor in strategic_nodes:
                neighbors_troop += troops_on_nodes[neighbor] * sum_of_score
                # strategic_nodes_with_score[neighbor]
            else:
                neighbors_troop += troops_on_nodes[neighbor]

        score = neighbors_troop * count_of_neighbors
        if node_id in strategic_nodes:
            score += (int(sum_of_score/6) -
                      my_nodes[node_id]) * strategic_nodes_with_score[node_id]
        else:
            score += - my_nodes[node_id]

        parametrs_for_build_up.update({node_id: score})
    parametrs_for_build_up = dict(
        sorted(parametrs_for_build_up.items(), key=lambda x: x[1], reverse=True))


# ============================================ turn ============================================
# function for get owners and troops in with redesign dictionary
def get_new_owners_turn(game):
    global dict_of_owners_with_troops, strategic_nodes_with_owner, troops_on_nodes, forts_on_nodes, my_nodes, my_id, owners_of_nodes, player_node_count
    owners_of_nodes = game.get_owners()
    troops_on_nodes = game.get_number_of_troops()
    forts_on_nodes = game.get_number_of_fort_troops()
    my_nodes = dict()
    p0 = 0
    p1 = 0
    p2 = 0
    for node_id in owners_of_nodes:
        owner_of_node = owners_of_nodes[node_id]
        troop_on_node = troops_on_nodes[node_id]
        fort_on_node = forts_on_nodes[node_id]

        # update strategic nodes
        if node_id in strategic_nodes_with_owner and owners_of_nodes[node_id] != strategic_nodes_with_owner[node_id]:
            strategic_nodes_with_owner.update(
                {node_id: owners_of_nodes[node_id]})

        # update dict of owners with troops
        if node_id not in dict_of_owners_with_troops or owners_of_nodes[node_id] != dict_of_owners_with_troops[node_id][0] or \
                troops_on_nodes[node_id] != dict_of_owners_with_troops[node_id][1] or forts_on_nodes[node_id] != dict_of_owners_with_troops[node_id][1]:
            dict_of_owners_with_troops.update(
                {node_id: [owner_of_node, troop_on_node, fort_on_node]})

        # update my nodes
        if owners_of_nodes[node_id] == my_id:
            my_nodes.update({node_id: [troop_on_node, fort_on_node]})

        # update player node count
        if owner_of_node == 0:
            p0 += 1
        elif owner_of_node == 1:
            p1 += 1
        elif owner_of_node == 2:
            p2 += 1
    player_node_count = {0: p0, 1: p1, 2: p2}


# function for get my nodes with special arrangement and we should attack from first node
def node_for_attack():
    global my_nodes, dict_of_owners_with_troops, strategic_nodes_with_score, node_for_attack_from
    for node_id in my_nodes:
        dict_of_strategic_neighbor = {}
        score_for_node_id = dict_of_owners_with_troops[node_id][1]
        for neighbor in strategic_nodes_with_score:
            if node_id != neighbor:
                distance = nx.shortest_path_length(
                    tiny_map_nx, node_id, neighbor)
                if distance == 1:
                    troops_on_neighbor_node = dict_of_owners_with_troops[neighbor]
                    dict_of_strategic_neighbor.update(
                        {neighbor: distance*(troops_on_neighbor_node[1]+troops_on_neighbor_node[2])})
                elif distance == 2:
                    for between_node in list(nx.all_shortest_paths(tiny_map_nx, node_id, neighbor)):
                        troops_on_neighbor_node = dict_of_owners_with_troops[between_node[1]]
                        dict_of_strategic_neighbor.update(
                            {between_node[1]: distance*(troops_on_neighbor_node[1]+troops_on_neighbor_node[2])})
                        if between_node[1] not in strategic_nodes_with_score:
                            score_for_node_id -= 25

                    troops_on_neighbor_node = dict_of_owners_with_troops[neighbor]
                    dict_of_strategic_neighbor.update(
                        {neighbor: distance*(troops_on_neighbor_node[1]+troops_on_neighbor_node[2])})

        for s_neighbor in dict_of_strategic_neighbor:
            if s_neighbor in strategic_nodes_with_score:
                score_for_node_id += 100 - \
                    dict_of_strategic_neighbor[s_neighbor]
            else:
                score_for_node_id -= dict_of_strategic_neighbor[s_neighbor]

        node_for_attack_from.update({node_id: score_for_node_id})

    node_for_attack_from = dict(
        sorted(node_for_attack_from.items(), key=lambda x: x[1], reverse=True))
    print(node_for_attack_from)


# function for get first node and attack to neighbors in special arrangement
def node_for_attack_target():
    global node_for_attack_from, strategic_nodes_with_score, tiny_map_nx, dict_of_owners_with_troops, node_for_attack_to, node_id_for_attack, my_id

    node_id_for_attack = next(iter(node_for_attack_from))
    node_distance = {}
    for s_node in strategic_nodes_with_score:
        distance = nx.shortest_path_length(
            tiny_map_nx, node_id_for_attack, s_node)
        if distance == 1:
            s_node_info = dict_of_owners_with_troops[s_node]
            if s_node_info[0] != my_id:
                node_distance.update(
                    {s_node: [distance, s_node_info[1]+s_node_info[2]]})
        elif distance == 2:
            s_node_info = dict_of_owners_with_troops[s_node]

    node_distance = dict(sorted(node_distance.items(),
                                key=lambda x: (x[0], x[1]), reverse=True))
    parametrs = {}
    for node_id in node_distance:
        if node_distance[node_id][0] == 1:
            if [(n) for n in list(nx.neighbors(tiny_map_nx, node_id)) if n in strategic_nodes]:
                parametrs.update({node_id: 0})
            else:
                parametrs.update({node_id: 1})
        else:
            parametrs.update({node_id: -1})
    parametrs = dict(
        sorted(parametrs.items(), key=lambda x: x[1], reverse=True))
    node_for_attack_to = list(parametrs.keys())
    print(node_for_attack_to)


def initializer(game: Game):
    # set global variables as a global variable
    global get_info, get_map, my_id, graph_of_map, tiny_map, graph_of_map_nx, tiny_map_nx, strategic_nodes, parameters, normal_parameters, parametrs_for_build_up, player_node_count, strategic_nodes_with_score, strategic_nodes_with_owner, owners_of_nodes, troops_on_nodes, my_nodes

    if get_info == False:
        # get player id
        my_id = game.get_player_id()['player_id']

        # get game map
        graph_of_map = game.get_adj()
        graph_of_map = convert_dict_from_int_to_str(graph_of_map)
        graph_of_map_nx = nx.Graph(graph_of_map)

        # get game strategic nodes and scores
        dict_of_strategic_nodes = game.get_strategic_nodes()
        strategic_nodes = dict_of_strategic_nodes['strategic_nodes']
        strategic_nodes = [str(item) for item in strategic_nodes]

        # convert strategic nodes with scores to two dictionary
        # first     key: node_id   value: score of node
        # second    key: node_id   value: troops
        for i in range(6):
            strategic_nodes_with_score.update(
                {str(dict_of_strategic_nodes['strategic_nodes'][i]): dict_of_strategic_nodes['score'][i]})
            strategic_nodes_with_owner.update(
                {str(dict_of_strategic_nodes['strategic_nodes'][i]): -1})

        # sort strategic_nodes_with_score by value in descending arrangement
        strategic_nodes_with_score = dict(
            sorted(strategic_nodes_with_score.items(), key=lambda x: x[1], reverse=True))

        make_tiny_map(graph_of_map)

        get_the_best_strategic_nodes()

    if get_info == True and get_map == False:
        # make map with strategic nodes and shortest path
        # make_map(graph_of_map)
        make_tiny_map(graph_of_map)

    # change flag
    get_info = True

    # get owners of nodes each time
    get_new_owners_initializer(game)
    print(owners_of_nodes)

    print("\nGo to put troops\n")
    # put first 2-6 troop on stratgic node
    for s_node_id in parameters:
        if strategic_nodes_with_owner[s_node_id] == -1:
            print(game.put_one_troop(s_node_id),
                  "-- putting one troop on", s_node_id)
            game.next_state()
            return

    # make function for put troops in neighbors of strategic nodes
    if not normal_parameters:
        get_the_best_normal_nodes()

    # put troop to tiny map normal nodes
    if -1 not in strategic_nodes_with_owner.values():
        for n_node_id in normal_parameters:
            if owners_of_nodes[n_node_id] == -1:
                print(game.put_one_troop(n_node_id),
                      "-- putting one troop on", n_node_id)
                game.next_state()
                return

    # print some information
    print(f"all player have {player_node_count} node")
    print(f"my_id is {my_id}")
    troops_on_nodes = game.get_number_of_troops()
    print(my_nodes)

    choice_node_for_build_up()
    print(f"\n\n{parametrs_for_build_up}\n\n")

    # put troop in best strategic node and build up it   (not name of node strategic only)
    for n_node_id in parametrs_for_build_up:
        print(game.put_one_troop(n_node_id),
              "-- putting one troop on", n_node_id)
        game.next_state()
        return


def turn(game: Game):
    global my_id, graph_of_map, tiny_map, graph_of_map_nx, tiny_map_nx, strategic_nodes, player_node_count, strategic_nodes_with_score, strategic_nodes_with_owner, troops_on_nodes, my_nodes, dict_of_owners_with_troops, node_for_attack_from, node_for_attack_to, node_id_for_attack

    # make fuction for map with troop count with all nodes
    get_new_owners_turn(game)
    print("Information is comming ....")
    print(dict_of_owners_with_troops, end='\n\n')
    print(strategic_nodes_with_score, end='\n\n')
    print(my_nodes, end='\n\n')
    print(tiny_map, end='\n\n')
    print(my_id, end='\n\n\n')

# start put troop session

    # make function for put troop to node for attack in tiny_map
    node_for_attack()
    node_for_attack_target()
    number_of_troops_to_put = game.get_number_of_troops_to_put()[
        'number_of_troops']
    game.put_troop(node_id_for_attack, number_of_troops_to_put)
    # 1 -> 2
    print(game.next_state())
# start attack session
    BETA_FRACTION = 2.4
    BETA_FRACTION_END = 0.41
    node_id_for_move_troop = []
    for node_id in node_for_attack_to:
        if node_id != node_for_attack_to[-1]:
            print(f"attack from {node_id_for_attack} to {node_id}")
            print(game.attack(node_id_for_attack, node_id, BETA_FRACTION, 0))
        else:
            print(f"attack from {node_id_for_attack} to {node_id}")
            print(game.attack(node_id_for_attack, node_id, BETA_FRACTION_END, 1))

            # {'message': 'attack successful', 'won': 1}
    # game.attack('1', '2', 0,)
    # make function for attack

    # 2 -> 3
    print(game.next_state())
# start move troop session

    # make function for move troops to strategic node for fort

    # 3 -> 4
    print(game.next_state())
# start fort session

    # make funciton for fort

    # 4 -> end turn
    print(tiny_map)
    print(my_nodes)
    print(game.next_state())
