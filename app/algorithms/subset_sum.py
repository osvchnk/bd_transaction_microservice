from typing import List


def subset_sum_recursive(numbers: List[int], target_sum: int) -> List[int] | None:
    """
    :param numbers: list of numbers
    :param target_sum: int
    :return: subset whose sum of numbers is closest or equal to target_sum
    """
    closest_sum = float('inf')
    closest_subset = []

    def subset_sum_helper(numbers, target_sum, current_sum, subset):
        nonlocal closest_sum, closest_subset

        if target_sum == 0:
            # Exact subset sum found
            closest_sum = 0
            closest_subset = subset[:]
            return

        if not numbers or target_sum < 0:
            # No subset found, update closest sum if necessary
            if abs(target_sum) < closest_sum:
                closest_sum = abs(target_sum)
                closest_subset = subset[:]
            return

        # Recursive cases
        num = numbers[0]
        remaining = numbers[1:]

        # Include the current number in the subset
        subset_sum_helper(remaining, target_sum - num, current_sum + num, subset + [num])

        # Exclude the current number from the subset
        subset_sum_helper(remaining, target_sum, current_sum, subset)

    subset_sum_helper(numbers, target_sum, 0, [])

    if closest_subset:
        return closest_subset
    else:
        return None
