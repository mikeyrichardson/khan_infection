from __future__ import division
import os
import unittest
from infection import total_infection
from infection import limited_infection

def generate_test_file(dir, file_name=None, num_users=10000, version='1.1',
                        user_to_coach_ratio=None, school_size=None,
                        uncoached_to_coached_ratio=1):

    ids = ['id{:013d}'.format(i) for i in xrange(num_users)]
    test_file_dir = dir
    if not os.path.isdir(test_file_dir):
        os.mkdir(test_file_dir)
    out_file_name = os.path.join(test_file_dir, file_name)
    out_file = open(out_file_name, 'w')

    if school_size and user_to_coach_ratio:
        for i, id in enumerate(ids):
            if i % user_to_coach_ratio == 0:
                lower = (i // school_size) * school_size + 1
                upper = lower + school_size
                offset = (i % school_size) // user_to_coach_ratio
                adj_list = ids[lower + offset:upper:uncoached_to_coached_ratio]
                out_file.write(id + '\t' + version + '\t' + ','.join(adj_list) + '\n')
            else:
                out_file.write(id + '\t' + version + '\t' + '\n')

    elif user_to_coach_ratio:
        for i, id in enumerate(ids):
            if i % user_to_coach_ratio == 0:
                lower = (i // user_to_coach_ratio) * user_to_coach_ratio + 1
                upper = lower + user_to_coach_ratio - 1
                adj_list = ids[lower:upper:uncoached_to_coached_ratio]
                out_file.write(id + '\t' + version + '\t' + ','.join(adj_list) + '\n')
            else:
                out_file.write(id + '\t' + version + '\t' + '\n')
    else:
        for i, id in enumerate(ids):
            out_file.write(id + '\t' + version + '\t' + '\n')

    out_file.close()


class InfectionTestCase(unittest.TestCase):
    """Tests for `infection.py`."""

    test_dir = 'test_files'
    test_file_configs = []

    @classmethod
    def setUpClass(cls):

        # Create a graph file where every hundredth person is a coach and coaches
        # half of the following 99 users.

        test_file_config = {
            'file_name': 'input_01.txt',
            'version': '1.1',
            'num_users': 10000,
            'user_to_coach_ratio': 100,
            'school_size': None,
            'uncoached_to_coached_ratio': 2
        }
        generate_test_file(cls.test_dir, **test_file_config)
        test_file_config['expected_test_total_infection'] = 51
        test_file_config['expected_test_limited_infection_percentage_10'] = 1000
        test_file_config['expected_test_limited_infection_amount_2019_tolerance_1_percent'] = 2019
        cls.test_file_configs.append(test_file_config)

        # Create a graph file with containing no edges

        test_file_config = {
            'file_name': 'input_03.txt',
            'version': '1.1',
            'num_users': 10000,
            'user_to_coach_ratio': None,
            'school_size': None,
            'uncoached_to_coached_ratio': None
        }
        generate_test_file(cls.test_dir, **test_file_config)
        test_file_config['expected_test_total_infection'] = 1
        test_file_config['expected_test_limited_infection_percentage_10'] = 1000
        test_file_config['expected_test_limited_infection_amount_2019_tolerance_1_percent'] = 2019
        cls.test_file_configs.append(test_file_config)

        # Create a graph file consisting of a single connected component

        test_file_config = {
            'file_name': 'input_02.txt',
            'version': '1.1',
            'num_users': 10000,
            'user_to_coach_ratio': 100,
            'school_size': 10000,
            'uncoached_to_coached_ratio': 2
        }
        generate_test_file(cls.test_dir, **test_file_config)
        test_file_config['expected_test_total_infection'] = 10000
        test_file_config['expected_test_limited_infection_percentage_10'] = 0
        test_file_config['expected_test_limited_infection_amount_2019_tolerance_1_percent'] = 0
        cls.test_file_configs.append(test_file_config)

        # Create a graph where edges occur only within groups of 2000 users

        test_file_config = {
            'file_name': 'input_04.txt',
            'version': '1.1',
            'num_users': 10000,
            'user_to_coach_ratio': 100,
            'school_size': 2000,
            'uncoached_to_coached_ratio': 20
        }
        generate_test_file(cls.test_dir, **test_file_config)
        test_file_config['expected_test_total_infection'] = 101
        test_file_config['expected_test_limited_infection_percentage_10'] = 0
        test_file_config['expected_test_limited_infection_amount_2019_tolerance_1_percent'] = 2000
        cls.test_file_configs.append(test_file_config)


    @classmethod
    def tearDownClass(cls):
        for config in cls.test_file_configs:
            os.remove(os.path.join(cls.test_dir, config['file_name']))
        if not os.listdir(cls.test_dir):
            os.rmdir(cls.test_dir)

    def test_total_infection(self):
        for config in self.test_file_configs:
            file_name = os.path.join(self.test_dir, config['file_name'])
            affected_users = total_infection(file_name, 'id0000000000001', '1.17')
            expected = config['expected_test_total_infection']
            self.assertEqual(len(affected_users), expected)

    def test_limited_infection_percentage_10__tolerance_0_percent(self):
        for config in self.test_file_configs:
            file_name = os.path.join(self.test_dir, config['file_name'])
            affected_users = limited_infection(file_name, '1.34', infection_percentage=0.1, 
                                               tolerance=0, userid=None)
            expected = config['expected_test_limited_infection_percentage_10']
            self.assertEqual(len(affected_users), expected)

    def test_limited_infection_percentage_20_19__tolerance_1_percent(self):
        for config in self.test_file_configs:
            file_name = os.path.join(self.test_dir, config['file_name'])
            affected_users = limited_infection(file_name, '1.34', infection_percentage=0.2019, 
                                               tolerance=0.01, userid=None)
            expected = config['expected_test_limited_infection_amount_2019_tolerance_1_percent']
            self.assertEqual(len(affected_users), expected)

if __name__ == '__main__':
    unittest.main()
