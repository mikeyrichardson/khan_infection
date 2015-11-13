import graph
import random
import os

# Assume user data is stored in a database and that
# all active userids, along with coach relationships
# can be extracted.

def total_infection(file_name, userid, version):
    """Change the website version of a user along with all related users.

    This function changes a user's version of the website and also changes
    the version of the user's students and coaches (and their students and coaches,
    and so on).

    Args:
        file_name (str): The name of the file containing the user data.
        version (str): The website version that users will be updated to.
        userid (str): All users related to this userid through coaching
            relationships will be updated to the same website version.
        datastore: The location of the datastore.
    """
    userid_adj_list_pairs = _extract_userids_and_adj_lists(file_name)
    gr = graph.SymbolGraph(iterable_input=userid_adj_list_pairs)
    cc = graph.ConnectedComponents(gr)
    user_cc_id = cc.get_cc_id(userid)
    cc_members = cc.get_nodes_with_cc_id(user_cc_id)
    return _update_version_for_users(file_name, cc_members, version)


def limited_infection(file_name, version, infection_percentage=0.1,
                      tolerance=0.05, userid=None):
    """Change the website version of a specified amount of active users.

    Args:
        file_name (str): The path of the file containing the data.
        version (str): The website version that infected users will be updated to.
        infection_percentage (float): The percentage of active users that should be infected.
        tolerance (float or int): Either a percentage (float) or absolute (int).
            The allowable discrepancy between the specified
            number of users to be infected and the actual amount. This allows the
            flexibility needed to ensure that coaches and students use the
            same version of the site.
        userid (str): The userid of a user that should be infected.

    Returns:
        The number of records updated.
    """
    users = _extract_userids_and_adj_lists(file_name)
    gr = graph.SymbolGraph(inpt=users)
    cc = graph.ConnectedComponents(gr)
    cc_counts = cc.get_cc_counts()
    desired_infections = int(gr.num_nodes * infection_percentage)

  
    # If a specific user is desired in the resulting set, remove that
    # user's connected component and find the remaining sum.
    if userid:
        user_cc_id = cc.get_cc_id(userid)
        user_cc_count = cc.get_count_for_cc_id(user_cc_id)
        cc_counts = cc_counts[:user_cc_id] + cc_counts[user_cc_id + 1:]
        desired_infections -= user_cc_count

    infected_cc_ids = _find_indices_of_subset(cc_counts, desired_infections,
                                              tolerance=tolerance)

    if infected_cc_ids is None:
        print ("Couldn't divide the connected components with desired " +
               "percentage infected: {:.1f}%, tolerance: {:.1f}%, and userid: {}"
              ).format(infection_percentage * 100, tolerance * 100, userid)
        return 0

    # Add the specified user's cc_id into the list of infected_cc_ids
    if userid:
        infected_cc_ids = [cc_id if cc_id < user_cc_id 
                                 else cc_id + 1 for cd_id in infected_cc_ids]

    users_to_update = []
    for cc_id in infected_cc_ids:
        users_to_update.extend(cc.get_nodes_with_cc_id(cc_id))
    return _update_version_for_users(file_name, users_to_update, version)


def _find_indices_of_subset(set_of_ints, target_sum, tolerance=0.0):
    """Find the indices of the set of numbers that add up to the
    given sum within the specified tolerance.

    Args:
        set_of_ints (list): list of non-negative integers
        sum (int): target sum
        tolerance (float): acceptable error for target sum, as a
                           decimal percentage
    """
    allowable_error = int(tolerance * target_sum)

    # sort the counts and remember the original order
    sorted_set_of_ints = sorted(set_of_ints, reverse=True)
    original_indices = sorted(range(len(set_of_ints)), key=lambda i: set_of_ints[i],
                              reverse=True)
    # There are likely to be a lot of connected components
    # with only one member. Remove the ones temporarily to
    # avoid excessive recursion in the _find_subset function.
    try:
        index_of_first_one = sorted_set_of_ints.index(1)
    except ValueError:
        index_of_first_one = len(sorted_set_of_ints)
    num_ones = len(sorted_set_of_ints) - index_of_first_one

    # See if the desired sum is possible
    lowest_acceptable_sum = target_sum - allowable_error - num_ones
    highest_acceptable_sum = target_sum + allowable_error
    set_of_ints_with_ones_removed = sorted_set_of_ints[:index_of_first_one]
    subset_indices = _find_subset(set_of_ints_with_ones_removed,
                                  lowest_acceptable_sum, 
                                  highest_acceptable_sum)
    if subset_indices is None:
        return None

    result_sum = sum(set_of_ints[i] for i in subset_indices)

    # Add back in the removed ones
    num_ones_needed = int(max(0, target_sum - result_sum))
    num_ones_used = min(num_ones_needed, num_ones)
    subset_indices = subset_indices + range(index_of_first_one,
                                            index_of_first_one + num_ones_used)

    # Convert the indices back to the pre-sort indices
    orig_subset_indices = [original_indices[i] for i in subset_indices]
    return orig_subset_indices
        

def _find_subset(set_of_ints, lower, upper):
    """ Iteratively find the indices of a subset that has a sum between lower and upper.

    Args:
        set_of_ints (list): The numbers that can be used in the subset.
        lower (int): The lowest acceptable sum for the subset.
        upper (int): The highest acceptable sum for the subset.

    Returns:
        list: A list of the indices of set_of_ints that were used to obtain the sum.
    """
    if upper < 0:
        return None
    if lower <=0 and 0 <= upper:
        return []
    reverse_sorted_set_of_ints = sorted(set_of_ints, reverse=True)
    original_indices = sorted(range(len(set_of_ints)), 
                              key=lambda i: set_of_ints[i],
                              reverse=True)
    current_sum = 0
    current_indices_int = 0
    i = 0
    reset_points = []
    most_recent_zero_location = -1
    while True:
        if i == len(reverse_sorted_set_of_ints):
            if len(reset_points) == 0:
                return None
            i, current_indices_int, current_sum = reset_points.pop()
            current_indices_int -= 2 ** i
            current_sum -= reverse_sorted_set_of_ints[i]
            i += 1
        current_sum += reverse_sorted_set_of_ints[i]
        if lower <= current_sum and current_sum <= upper:
            current_indices_int += 2 ** i
            found_indices = convert_to_list_of_indices(current_indices_int)
            orig_subset_indices = [original_indices[i] for i in found_indices]
            return orig_subset_indices
        elif current_sum > upper:
            if i > 0 and i > most_recent_zero_location + 1:
                reset_points.append((i - 1, current_indices_int, current_sum))
            most_recent_zero_location = i
            current_sum -= reverse_sorted_set_of_ints[i]
        else:
            current_indices_int += 2 ** i
        i += 1

def convert_to_list_of_indices(num):
    indices = []
    i = 0
    while num > 0:
        if num % 2 == 1:
            indices.append(i)
        num = num // 2
        i += 1
    return indices


# # This recursive version would surpass the recursion depth limit too often
# def _find_subset(set_of_ints, lower, upper, index=0, subset_indices=None):
#     """Recursively find a subset that sums to a value between lower and upper.

#     Args:
#         set_of_ints (list): The numbers that can be used in the subset.
#         lower (int): The lowest acceptable sum for the subset.
#         upper (int): The highest acceptable sum for the subset.
#         index (int): The index in set_of_ints that should next be added to the subset.
#         subset_indices (list): The indices of the current subset.

#     Returns:
#         list: A list of the indices of set_of_ints that were used to obtain the sum.
#     """
#     if subset_indices is None:
#         subset_indices = []
#     if upper < 0:
#         return None
#     if lower <= 0 and 0 <= upper:
#         return subset_indices
#     for i in xrange(index, len(set_of_ints)):
#         found_indices = _find_subset(set_of_ints, 
#                                      lower - set_of_ints[i], 
#                                      upper - set_of_ints[i],
#                                      index + 1, 
#                                      subset_indices + [i])
#         if found_indices is not None:
#             return found_indices
#     return None


# This would be a function to extract the info from
# a database
def _extract_userids_and_adj_lists(file_name):
    in_file = open(file_name)
    for line in in_file:
        fields = line[:-1].split('\t')
        userid = fields[0]
        if len(fields) == 2:
            yield (userid, None)
        else:
            adj_list = fields[2].split(',')
            yield (userid, adj_list)
    in_file.close()


# This would be a function to update the database
def _update_version_for_users(in_file_name, affected_users, version):
    """
    Connect to database and update the version of each record
    corresponding to the ids in users.
    """
    out_file_name = 'tmp{}'.format(random.randint(10000000,99999999))
    out_file = open(out_file_name, 'w')
    in_file = open(in_file_name)
    for line in in_file:
        fields = line.split('\t')
        userid = fields[0]
        if userid in affected_users:
            out_file.write(userid + '\t' + version + '\t' + '\t'.join(fields[2:]))
        else:
            out_file.write(line)
    in_file.close()
    out_file.close()
    os.remove(in_file_name)
    os.rename(out_file_name, in_file_name)
    return len(affected_users)
