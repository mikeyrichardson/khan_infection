class SymbolGraph(object):
    def __init__(self, file_path = None):
        self.num_nodes = 0
        self.num_edges = 0
        self.symbol_dict = {}
        self.inverse_symbol_dict = []
        self.adj_lists = []
        if file_path:
            self.read_graph_from_file(file_path)

    def add_node(self, node_name):
        if node_name in self.symbol_dict:
            return
        else:
            node = len(self.inverse_symbol_dict)
            self.symbol_dict[node_name] = node
            self.inverse_symbol_dict.append(node_name)
            self.adj_lists.append([])
            self.num_nodes += 1

    def add_edge(self, src_node_name, dest_node_name):
        self.add_node(src_node_name)
        self.add_node(dest_node_name)
        src_node = self.symbol_dict[src_node_name]
        dest_node = self.symbol_dict[dest_node_name]
        self.adj_lists[src_node].append(dest_node)
        if src_node != dest_node:
            self.adj_lists[dest_node].append(src_node)
        self.num_edges += 1

    def read_graph_from_file(self, file_path):
        file = open(file_path)
        for line in file:
            node_name, neighbor_list = line[:-1].split('\t')
            if neighbor_list:
                neighbor_names = neighbor_list.split(',')
                for neighbor_name in neighbor_names:
                    self.add_edge(node_name, neighbor_name)
            else:
                self.add_node(node_name)
        file.close()


class ConnectedComponents(object):
    def __init__(self, graph):
        self.graph = graph
        self.visited = [False] * self.graph.num_nodes
        self.cc_id = [-1] * self.graph.num_nodes
        self.cc_id_membership_list = [[]]
        self.current_cc_id = 0
        self.current_cc_count = 0
        self.cc_counts = []
        for node in xrange(self.graph.num_nodes):
            if self.visited[node]:
                continue
            else:
                self.dfs(node)
                self.cc_counts.append(self.current_cc_count)
                self.current_cc_id += 1
                self.current_cc_count = 0
                self.cc_id_membership_list.append([])

    def dfs(self, node):
        if self.visited[node]:
            return
        self.visited[node] = True
        self.cc_id[node] = self.current_cc_id
        self.cc_id_membership_list[self.current_cc_id].append(node)
        self.current_cc_count += 1
        for neighbor in self.graph.adj_lists[node]:
            self.dfs(neighbor)

    def get_cc_id(self, node_name):
        return self.cc_id[symbol_dict[node_name]]

    def get_num_ccs(self):
        return self.current_cc_id

    def get_cc_counts(self):
        return self.cc_counts[:]

    def get_count_for_cc_containing_node(self, node_name):
        return self.cc_counts[self.cc_id[self.symbol_dict[node_name]]]

    def get_count_for_cc_id(self, id):
        return self.cc_counts[id]

    def get_list_of_nodes_with_cc_id(self, id):
        node_names = []
        for node in self.cc_id_membership_list[id]:
            node_names.append(self.inverse_symbol_dict[node])
        return node_names



