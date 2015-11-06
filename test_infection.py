from __future__ import division
import os
import unittest
from infection import total_infection
from infection import limited_infection

test_file_list = None

def generate_test_files(dir, num_nodes=10000, version='1.1',
                        node_with_edges_frequency=100, group_size=2000):

    ids = ['id{:013d}'.format(i) for i in xrange(num_nodes)]
    test_files_path = dir
    if not os.path.isdir(test_files_path):
        os.mkdir(test_files_path)

    info_test_files = {}

    # Create a graph file where every `node_with_edges_frequency` node is connected to half
    # of the `node_with_edges_frequency - 1` following nodes. Each connected component will 
    # have `node_with_edges_frequency / 2 + 1` nodes.
    out_file_name = os.path.join(test_files_path, 'test_input_01.txt')
    out_file = open(out_file_name, 'w')
    info_test_files[out_file_name] = {}
    info_test_files[out_file_name]['num_nodes'] = len(ids)
    info_test_files[out_file_name]['num_edges'] = 0
    for i, id in enumerate(ids):
        if i % node_with_edges_frequency == 0:
            lower = (i // node_with_edges_frequency) * node_with_edges_frequency + 1
            upper = lower + node_with_edges_frequency - 1
            adj_list = ids[lower:upper:2]
            info_test_files[out_file_name]['num_edges'] += len(adj_list)
        else:
            adj_list = []
        out_file.write(id + '\t' + version + '\t' + ','.join(adj_list) + '\n')
    out_file.close()

    # Create a graph file consisting of only nodes (no edges)
    out_file_name = os.path.join(test_files_path, 'test_input_02.txt')
    out_file = open(out_file_name, 'w')
    info_test_files[out_file_name] = {}
    info_test_files[out_file_name]['num_nodes'] = len(ids)
    info_test_files[out_file_name]['num_edges'] = 0
    for id in ids:
        out_file.write(id + '\t' + version + '\t' + '\n')
    out_file.close()

    # Create a graph file consisting of a single connected component
    out_file_name = os.path.join(test_files_path, 'test_input_03.txt')
    out_file = open(out_file_name, 'w')
    info_test_files[out_file_name] = {}
    info_test_files[out_file_name]['num_nodes'] = len(ids)
    info_test_files[out_file_name]['num_edges'] = 0
    for i, id in enumerate(ids):
        if i % node_with_edges_frequency == 0:
            lower = (i // node_with_edges_frequency) * node_with_edges_frequency + 1
            upper = lower + node_with_edges_frequency
            adj_list = ids[lower:upper]
            info_test_files[out_file_name]['num_edges'] += len(adj_list)
        else:
            adj_list = []
        out_file.write(id + '\t' + version + '\t' + ','.join(adj_list) + '\n')
    out_file.close()

    # Create a graph where edges occur only between `group_size` contiguous nodes
    out_file_name = os.path.join(test_files_path, 'test_input_04.txt')
    out_file = open(out_file_name, 'w')
    info_test_files[out_file_name] = {}
    info_test_files[out_file_name]['num_nodes'] = len(ids)
    info_test_files[out_file_name]['num_edges'] = 0
    interval = group_size // node_with_edges_frequency
    for i, id in enumerate(ids):
        if i % node_with_edges_frequency == 0:
            lower = (i // group_size) * group_size + 1
            upper = lower + group_size
            offset = (i % group_size) // node_with_edges_frequency
            adj_list = ids[lower + offset:upper:interval]
            info_test_files[out_file_name]['num_edges'] += len(adj_list)
        else:
            adj_list = []
        out_file.write(id + '\t' + version + '\t' + ','.join(adj_list) + '\n')
    out_file.close()

    return info_test_files

class InfectionTestCase(unittest.TestCase):
    """Tests for `infection.py`."""

    def test_total_infection(self):
        correct_num_affected_users = [51, 1, 10000, 101]
        for i, file_name in enumerate(test_file_list):
            affected_users = total_infection(file_name, 'id0000000000001', '1.17')
            self.assertEqual(affected_users, correct_num_affected_users[i])

    def test_limited_infection_percentage_10(self):
        correct_num_affected_users = [1000, 1000, 0, 0]
        for i, file_name in enumerate(test_file_list):
            affected_users = limited_infection(file_name, '1.34', percentage=0.1, 
                                             amount=None, tolerance=0, userid=None)
            self.assertEqual(affected_users, correct_num_affected_users[i])

    def test_limited_infection_amount_2019_tolerance_1_percent(self):
        correct_num_affected_users = [2019, 2019, 0, 2000]
        for i, file_name in enumerate(test_file_list):
            affected_users = limited_infection(file_name, '1.34', percentage=None, 
                                             amount=2019, tolerance=0.01, userid=None)
            self.assertEqual(affected_users, correct_num_affected_users[i])


if __name__ == '__main__':
    dir = 'test_files'
    test_files_info = generate_test_files(dir, num_nodes=10000, version='1.1',
                        node_with_edges_frequency=100, group_size=2000)
    test_file_list = sorted(test_files_info.keys())
    unittest.main()
    for file_name in test_files_info:
        os.remove(file_name)
    if not os.listdir(dir):
        os.rmdir(dir)
