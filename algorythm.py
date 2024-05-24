'''
types of nodes:
start - node, when crawler places
finish - final node
default - default node
key_hoalder - node with key and weight to earn it
'''
import random
import random
import networkx as nx
import matplotlib.pyplot as plt
import time


#метод, который будет визуализировать граф, меняя его цвет относительно текущих значений метрики
def draw_action(nodes, ways):
    G = nx.DiGraph()
    color_map = []

    for node in nodes:
        G.add_node(node.number, type=node.type_of_node)
        color_map.append(node.metrix)

    for way in ways:
        G.add_edge(way.node_from.number, way.node_to.number, duration=way.duration, gates=list(way.gates))

    pos = nx.spring_layout(G)
    norm = plt.Normalize(min(color_map), max(color_map))
    colors = plt.cm.viridis(norm(color_map))

    plt.figure(figsize=(12, 8))
    ax = plt.gca()
    nx.draw(G, pos, with_labels=True, node_color=colors, node_size=500, cmap=plt.cm.viridis, ax=ax)
    labels = nx.get_edge_attributes(G, 'duration')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=ax)
    sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ax=ax)
    plt.show()


class Node:
    def __init__(self, number, type_of_node, keys):
        self.ways_to_go = set()
        self.ant_counter = 0
        self.number = number
        self.score = 0
        self.type_of_node = type_of_node
        self.keys = set()
        self.metrix = 0

    def add_key(self, key):
        self.keys.add(key)

    def add_way(self, way):
        self.ways_to_go.add(way)

    def __repr__(self):
        return 'Node number:' + str(
            self.number + 1) + '\n' + 'Node type:' + self.type_of_node + '\n' + 'Ways to:' + '\n\t' + '\n\t'.join(
            map(str, self.ways_to_go)) + '\nKeys: ' + ' '.join(map(str, self.keys)) + '\n\nScore:' + str(
            self.score) + '\n\n'


class Way:
    def __init__(self, node_from, duration, node_to):
        self.node_from = node_from
        self.node_to = node_to
        self.duration = duration
        self.gates = set()

    def check(self, antie):
        biba = set()
        hehe = []
        for i in antie.keys:
            hehe.append(type(i))

        for i in antie.keys:
            biba.add(i.value)
        return self.gates.issubset(biba)

    def add_gates(self, gates):
        self.gates.add(gates)

    def __repr__(self):
        return ''.join(
            list(map(str,
                     [self.node_from.number, '-->', self.node_to.number, ' | duration:', self.duration, ' | gates:',
                      ' '.join(map(str, self.gates))])))

    def __str__(self):
        return ''.join(
            list(map(str,
                     [self.node_from.number, '-->', self.node_to.number, ' | duration:', self.duration, ' | gates:',
                      ' '.join(map(str, self.gates))])))


'''
3)посчитать метрику
реализвать инициализацию ключей для муравьишек, с которыми они стартуют
'''


class Key:
    def __init__(self, value):
        self.value = value
        self.score = 0

    def __repr__(self):
        return str(self.value) + ' '


class Ant:
    def __init__(self, number, cur_node, turns, keys):
        self.number = number
        self.score = 0
        self.turns = turns
        self.keys = keys
        self.current_node = cur_node
        self.path = set()
        self.ways = set()
        self.available = set()
        for i in cur_node.ways_to_go:
            self.available.add(i)

    def turn(self):
        if self.current_node.type_of_node == 'key_holder':
            [self.keys.add(i) for i in self.current_node.keys]
            new_available = self.available.copy()
            for way in self.available:
                for predict in way.node_from.ways_to_go:
                    if predict.check(self) and predict.node_to not in self.path:
                        new_available.add(predict)
            self.turns -= 1
            self.available = new_available
        if self.current_node.type_of_node == 'finish':
            for i in self.path:
                i.score += len(self.path) / self.score
                i.ant_counter += 1
            self.current_node.score += len(self.path) / self.score
            self.current_node.ant_counter += 1
            return
        else:
            self.turns -= 1
            if self.turns == 0:
                return
        self.path.add(self.current_node)
        self.move()
        self.turn()

    def move(self):

        curwa = random.choice(list(self.available))
        for i in curwa.gates:
            for j in self.keys:
                if j.value == i:
                    j.score += 1
        self.score += curwa.duration
        self.current_node = curwa.node_to
        for i in self.current_node.ways_to_go:
            if i.check(self):
                self.available.add(i)


def matrix_to_graph(adj_matrix, node_types, node_keys=None, way_gates=None):
    nodes = []
    ways = []
    nodes_start = []

    if node_keys is None:
        node_keys = {}
    if way_gates is None:
        way_gates = {}

    for i in range(len(adj_matrix)):
        node = Node(i, node_types[i], set())  # Создаем узел с указанным типом
        if node_types[i] == 'start':
            nodes_start.append(node)


        elif node_types[i] == 'key_holder':
            # Если для узла типа key_holder переданы ключи, добавляем их
            if i in node_keys:
                for key in node_keys[i]:
                    node.add_key(key)

        nodes.append(node)

    for i in range(len(adj_matrix)):
        for j in range(len(adj_matrix[i])):
            if adj_matrix[i][j] != 0:
                way = Way(nodes[i], adj_matrix[i][j], nodes[j])
                # Если для пути есть ворота, добавляем их
                if (i, j) in way_gates:
                    for gate in way_gates[(i, j)]:
                        way.add_gates(gate)
                ways.append(way)

    for way in ways:
        way.node_from.add_way(way)
    everything = nodes.copy()
    for nd in nodes:
        if nd.type_of_node in {'start', 'finish'}:
            nodes.remove(nd)
    return nodes_start, nodes, ways, everything


def MURAVINNAYA_PUSKOVAYA_USTANOVKA_3000(ant_amount, number_of_ant_iteration, start_nodes, nodes, keys, everykey,
                                         graph):
    cond_keys = keys.copy()
    for i in range(ant_amount):
        ant = Ant(i + 1, random.choice(list(start_nodes)), number_of_ant_iteration, keys)
        ant.turn()
    print(node_metrix_counter(graph))
    print(key_metrix_counter(everykey, cond_keys))


def node_metrix_counter(nodes):
    for i in nodes:
        i.metrix = i.score / i.ant_counter
    nodes.sort(key=lambda x: x.metrix, reverse=True)
    draw_action(nodes, ways)  #отрисовка графа

    biba = []
    for i in nodes:
        if i.type_of_node not in ['key_holder', 'start', 'finish']:
            biba.append(i)
    return biba


def key_metrix_counter(keys, ant_keys):
    biba = sorted(keys, key=lambda x: x.score, reverse=True)
    boba = ''
    for i in biba:
        if i not in ant_keys:
            boba += str(i.value) + ':' + str(i.score) + ', '
    return boba


if __name__ == '__main__':
    matrix = [[0, 2, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
              [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 0],
              [0, 2, 0, 0, 0, 5, 0, 0, 0, 1, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
              [0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 1, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    types = ['start', 'default', 'default', 'default', 'default',
             'default', 'default', 'default', 'finish', 'key_holder', 'key_holder', 'key_holder', 'key_holder']
    keys = [Key(2), Key(6), Key(4), Key(5), Key(1), Key(3)]
    key_points = {10: {keys[2], keys[0]}, 11: {keys[0], keys[1]}, 12: {keys[1]}, 13: {keys[3]}}
    gates = {(0, 1): {1, 3}, (0, 3): {1}, (0, 6): {1}, (3, 5): {1}, (5, 7): {1}, (7, 8): {1}, (2, 8): {6}, (2, 4): {2},
             (4, 8): {5}}

    ant_keys = {keys[5], keys[4]}
    nodes_start, nodes, ways, graph = matrix_to_graph(matrix, types, key_points, gates)
    MURAVINNAYA_PUSKOVAYA_USTANOVKA_3000(1000, 10, nodes_start, nodes, ant_keys, keys, graph)
