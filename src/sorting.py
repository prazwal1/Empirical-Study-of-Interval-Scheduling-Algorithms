def merge_sort(jobs, dimension=0):
    if len(jobs) <= 1:
        return jobs
    mid = len(jobs) // 2
    left = merge_sort(jobs[:mid], dimension)
    right = merge_sort(jobs[mid:], dimension)
    return merge(left, right, dimension)

def merge(left, right, dimension):
    sorted_arr = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i][dimension] < right[j][dimension]:
            sorted_arr.append(left[i])
            i += 1
        else:
            sorted_arr.append(right[j])
            j += 1
    sorted_arr.extend(left[i:])
    sorted_arr.extend(right[j:])
    return sorted_arr


def merge_sort_by_duration(jobs):
    if len(jobs) <= 1:
        return jobs
    mid = len(jobs) // 2
    left = merge_sort_by_duration(jobs[:mid])
    right = merge_sort_by_duration(jobs[mid:])
    return merge_by_duration(left, right)

def merge_by_duration(left, right):
    sorted_arr = []
    i = j = 0
    while i < len(left) and j < len(right):
        left_duration = left[i][1] - left[i][0]
        right_duration = right[j][1] - right[j][0]
        if left_duration < right_duration:
            sorted_arr.append(left[i])
            i += 1
        else:
            sorted_arr.append(right[j])
            j += 1
    sorted_arr.extend(left[i:])
    sorted_arr.extend(right[j:])
    return sorted_arr