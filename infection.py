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
    users = _extract_userids_and_adj_lists(file_name)
    gr = graph.SymbolGraph(inpt=users)
    cc = graph.ConnectedComponents(gr)
    user_cc_id = cc.get_cc_id(userid)
    cc_members = cc.get_nodes_with_cc_id(user_cc_id)
    return _update_version_for_users(file_name, cc_members, version)


def limited_infection(file_name, version, percentage=0.1, amount=None,
                      tolerance=0.01, userid=None):
    """Change the website version of a specified amount of active users.

    Args:
        version (str): The website version that selected users will be updated to.
        userid (str): The userid of a user that should be selected.
        percentage (float): The percentage of active users that should be selected.
            Does nothing if amount is specified.
        amount (int): The amount of users that should be selected.
        tolerance (float or int): Either a percentage (float) or absolute (int).
            The allowable discrepancy between the specified
            number of users to be infected and the actual amount. This allows the
            flexibility needed to ensure that coaches and students use the
            same version of the site.
        datastore: The location of the datastore.

    Returns:
        The number of records updated.
    """
    users = _extract_userids_and_adj_lists(file_name)
    gr = graph.SymbolGraph(inpt=users)
    cc = graph.ConnectedComponents(gr)
    cc_counts = cc.get_cc_counts()
    if amount:
        desired_amount_infected_users = amount
    else:
        desired_amount_infected_users = int(gr.num_nodes * percentage)

    # If a specific user is desired in the resulting set, remove that
    # user's connected component and find the remaining sum.
    if userid:
        user_cc_id = cc.get_cc_id(userid)
        user_cc_count = cc.get_count_for_cc_id(user_cc_id)
        cc_counts = cc_counts[:user_cc_id] + cc_counts[user_cc_id + 1:]
        desired_amount_infected_users -= user_cc_count

    amount_of_users_in_subset, cc_ids = \
        _find_indices_of_subset_with_sum(cc_counts, desired_amount_infected_users,
                                        tolerance=tolerance)

    if amount_of_users_in_subset is None:
        print ("Couldn't divide the connected components with desired amount infected: {}, " +
              "tolerance: {:.1f}%, and userid: {}").format(desired_amount_infected_users,
                                                           tolerance * 100, userid)
        return 0

    # Add the specified user's cc_id into the list of cc_ids
    if userid:
        amount_of_users_in_subset += user_cc_count
        cc_ids = [cc_id if cc_id < user_cc_id else cc_id + 1 for cd_id in cc_ids]

    users_to_update = []
    for cc_id in cc_ids:
        users_to_update.extend(cc.get_nodes_with_cc_id(cc_id))
    return _update_version_for_users(file_name, users_to_update, version)


def _find_indices_of_subset_with_sum(nums, target_sum, tolerance=0.0):
    """Find the indices of the set of numbers that add up to the
    given sum within the specified tolerance.

    Args:
        nums (list): list of numbers
        sum (int): target sum
        tolerance (Optional[float,int]): acceptable error for target sum,
            either a percentage (float) or absolute (int)
    """
    if type(tolerance) == float:
        tolerance = int(tolerance * target_sum)

    # sort the counts and remember the original order
    sorted_nums = sorted(nums, reverse=True)
    original_indices = sorted(range(len(nums)), key=lambda i: nums[i],
                              reverse=True)
    # There are likely to be a lot of connected components
    # with only one member. Remove the ones temporarily to
    # avoid excessive recursion.
    try:
        index_of_first_one = sorted_nums.index(1)
    except ValueError:
        index_of_first_one = len(sorted_nums)
    num_ones = len(sorted_nums) - index_of_first_one

    # See if the desired sum is possible
    lowest_acceptable_sum = target_sum - tolerance - num_ones
    highest_acceptable_sum = target_sum + tolerance
    nums_without_the_ones = sorted_nums[:index_of_first_one]
    result_sum, subset_indices = \
        _find_sum_in_bounds(nums_without_the_ones,
                            lowest_acceptable_sum, highest_acceptable_sum)
    if result_sum is  None:
        return None, []

    # Add back in the removed ones
    num_ones_needed = int(max(0, target_sum - result_sum))
    num_ones_used = min(num_ones_needed, num_ones)
    subset_indices = subset_indices + range(index_of_first_one,
                                            index_of_first_one + num_ones_used)

    return result_sum + num_ones_used, \
        [original_indices[i] for i in subset_indices]


def _find_sum_in_bounds(nums, lower, upper, index=0,
                                    current_sum=0, subset_indices=[]):
    """Recursively find a subset that sums to a value between lower and upper.

    Args:
        nums (list): The numbers that can be used in the subset.
        lower (int): The lowest acceptable sum for the subset.
        upper (int): The highest acceptable sum for the subset.
        index (int): The index in nums that should next be added to the sum.
        current_sum (int): The sum of the current subset.
        subset_indices (list): The indices of the current subset.

    Returns:
        int: A sum between lower and higher (or None if no such sum is possible).
        list: A list of the indices of nums that were used to obtain the sum.
    """
    if current_sum == 0 and current_sum >= lower:
        return 0, []
    if current_sum > upper:
        return None, []
    for i in xrange(index, len(nums)):
        next_sum = current_sum + nums[i]
        if next_sum >= lower and next_sum <= upper:
            subset_indices.append(i)
            return next_sum, subset_indices
        elif next_sum < lower:
            found_sum, indices = \
                _find_sum_in_bounds(nums, lower, upper, index + 1,
                                    next_sum, subset_indices[:] + [i])
            if found_sum:
                return found_sum, indices
        return None, []


# This would be a function to extract the info from
# a database
def _extract_userids_and_adj_lists(file_name):
    in_file = open(file_name)
    for line in in_file:
        fields = line[:-1].split('\t')
        if len(fields) == 2:
            yield fields[0] + '\t\n'
        else:
            yield fields[0] + '\t' + fields[2] + '\n'
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
