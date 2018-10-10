# -*- coding: utf-8 -*-

def find_outlier(integers):
    odd_list = []
    even_list = []
    result = None
    for num in integers:
        if num % 2 == 0:
            even_list.append(num)
        else:
            odd_list.append(num)
        if len(odd_list) * len(even_list) >= 2:
            result = odd_list[0] if len(odd_list) == 1 else even_list[0]
            break
    return result


def solution(s):
    result_list = []
    result_str = ""
    if len(s) > 0:
        for index, string in enumerate(s):
            result_str +=string
            if index % 2 == 1 and index < len(s) - 1:
                result_str += ","
        result_list = result_str.split(",")
        result_list[-1] = result_list[-1] + "_" if len(result_list[-1]) == 1 else result_list[-1]
    return result_list


def find_even_index(arr):
    result = -1
    result_list = []
    arr_list = list(arr)
    for index in range(len(arr_list)):
        first_half = sum(arr_list[:index])
        second_half = sum(arr_list[index+1:])
        if first_half == second_half:
            result_list.append(index)
    if len(result_list) > 0:
        result = result_list[0]
    return result


def dirReduc(arr):
    opposite_dict = {"NORTH": "SOUTH", "SOUTH": "NORTH", "EAST": "WEST", "WEST":"EAST"}
    result = arr
    new_arr = []
    while result != new_arr:
        new_arr = result
        result = []
        index = 0
        while index < len(new_arr) - 1:
            if new_arr[index] == opposite_dict[new_arr[index+1]]:
                index += 2
            elif new_arr[index] == new_arr[index+1]:
                result.append(new_arr[index])
                index += 1
            else:
                result.append(new_arr[index])
                index += 1
        result.append(new_arr[-1])
    return result

# wonderful result
def dirReduc_clever(plan):
    new_plan = []
    for d in plan:
        if new_plan and new_plan[-1] == opposite[d]:
            new_plan.pop()
        else:
            new_plan.append(d)
    return new_plan

def format_duration(seconds):
    result = None
    result_list = []
    year = seconds / (365 * 24* 60 * 60)
    if year == 1:
        year_str = str(year) + " year"
        result_list.append(year_str)
    elif year > 1:
        year_str = str(year) + " years"
        result_list.append(year_str)
    days = (seconds %  (365 * 24 * 60 * 60)) / (24 * 60 * 60)
    if days == 1:
        day_str = str(days) + " day"
        result_list.append(day_str)
    elif days > 1:
        day_str = str(days) + " days"
        result_list.append(day_str)
    hours = (seconds % (24 * 60 * 60)) / (60 * 60)
    if hours == 1:
        hour_str = str(hours) + " hour"
        result_list.append(hour_str)
    elif hours > 1:
        hour_str = str(hours) + " hours"
        result_list.append(hour_str)
    minutes = (seconds % 3600) / 60
    if minutes == 1:
        minute_str = str(minutes) + " minute"
        result_list.append(minute_str)
    elif minutes > 1:
        minute_str = str(minutes) + " minutes"
        result_list.append(minute_str)
    second = seconds % 60
    if second == 1:
        second_str = str(second) + " second"
        result_list.append(second_str)
    elif second > 1:
        second_str = str(second) + "seconds"
        result_list.append(second_str)
    if len(result_list) > 2:
        result = ", ".join(result_list[:-1]) + " and " + result_list[-1]
    elif len(result_list) == 2:
        result = result_list[0] + " and " + result_list[1]
    else:
        result = result_list[0]
    return result


def format_duration_clever(seconds):
    """
    思想跟我自己写的函数一样的，但是写的形式比我写的简洁多了，学习
    :param seconds:
    :return:
    """
    times = [("year", 365 * 24 * 60 * 60),
             ("day", 24 * 60 * 60),
             ("hour", 60 * 60),
             ("minute", 60),
             ("second", 1)]
    if not seconds:
        return "now"

    chunks = []
    for name, secs in times:
        qty = seconds // secs
        if qty:
            if qty > 1:
                name += "s"
            chunks.append(str(qty) + " " + name)

        seconds = seconds % secs

    return ', '.join(chunks[:-1]) + ' and ' + chunks[-1] if len(chunks) > 1 else chunks[0]


def sum_pairs(ints, s):
    for i in range(1, len(ints)):
        for j in range(len(ints)-i):
            if ints[j] + ints[i+j] == s:
                return [ints[j], ints[i+j]]
    return None

def sum_pairs_clever(ints, s):
    """
    运用了set不可重复的特点，值得学习的例子
    :param ints:
    :param s:
    :return:
    """
    result_set = set()
    for i in ints:
        if s - i in result_set:
            return [i, s-i]
        result_set.add(i)

def fibonacci(n):
    fib_list = [0, 1]
    i = 2
    while i <= n:
        i += 1
        fib_list.append(fib_list[-1] + fib_list[-2])
        if fib_list > 4:
            del fib_list[0]
    return fib_list[-1]


def is_valid_coordinates(coordinates):
    result = False
    coordinates_list = coordinates.split(",")
    if len(coordinates_list) == 2:
        result_1 = is_valid_index(coordinates_list[0], 90)
        coordinate_2 = coordinates_list[1].split(" ")
        if len(coordinate_2) > 2:
            return False
        elif len(coordinate_2) == 2 and coordinate_2[0] != "":
            return False
        else:
            coordinate_2 = coordinate_2[-1]
        result_2 = is_valid_index(coordinate_2,180)
        result = result_1 and result_2
    return result

def is_valid_index(coordinate, range_num):
    i = 0
    j = 0
    if coordinate[0] == "-":
        str_list = coordinate[1:]
    else:
        str_list = coordinate
    for str_num in str_list:
        if str_num == ".":
            i += 1
        if str_num == "-":
            j += 1
        if str_num not in str_list:
            return False
        if i > 1 or j > 0:
            return False
    if abs(float(coordinate)) <= range_num:
        return True
    else:
        return False


def is_valid_coordinates_clever(coordinates):
    # 这个习题让我很好的学习了try, except函数，“e"的考虑在于，python会将1e1读成是一个数字
    # 值得学习的一道题
    try:
        lat, lng = [abs(float(c)) for c in coordinates.split(',') if "e" not in c]
    except ValueError:
        return False

    return lat <= 90 and lng <= 180

def is_valid_coordinates_clever2(s):
    try:
        a, b = s.split(',')
        if 'e' in a or 'e' in b: raise Exception
        a, b = float(a), float(b)
        return abs(a)<=90 and abs(b)<=180
    except:
        return False

import itertools
def choose_best_sum(t, k, ls):
    sorted_ls = sorted(ls)
    if sum(sorted_ls[:k]) > t or len(ls) < k:
        return None
    else:
        sum_num = sum(sorted_ls[:k])
        for choose_num in itertools.combinations(ls, k):
            new_sum_num = sum(choose_num)
            sum_num = new_sum_num if sum_num < new_sum_num <= t else sum_num
        return sum_num


import numpy as np
def validSolution(board):
    board_arr = np.array(board)
    for i in range(9):
        if not (valid_list(board_arr[i, :]) and valid_list(board_arr[:, i])):
            return False
    for i in range(0, 7, 3):
        for j in range(0, 7, 3):
            flat_list = board_arr[i:i+3, j:j+3].flatten()
            if not valid_list(flat_list):
                return False
    return True

def valid_list(list):
    if len(list) != len(set(list)):
        return False
    return True


# 这道题挺难的，花了接近一天的时间，主要的突破点在于解决递归这个问题
# 还有一个问题就是python中的copy问题，否则一个变量的改变会带来另一个变量的改变
def find_word(board, word):
    board_arr = np.array(board)
    result = get_word_index(board_arr, word)
    if len(result) > 0:
        return True
    return False


def get_word_index(board_arr, word):
    result = []
    if len(word) == 1:
        index_stamp_list = np.argwhere(board_arr == word)
        for index_stamp in index_stamp_list:
            result.append([list(index_stamp)])
    else:
        pre_word_index_list = get_word_index(board_arr, word[:-1])
        if len(pre_word_index_list) > 0:
            for pre_word_index in pre_word_index_list:
                index_stamp_list = np.argwhere(board_arr == word[-1])
                for index_stamp in index_stamp_list:
                    new_pre_word_index = [i for i in pre_word_index]
                    if list(index_stamp) not in pre_word_index and  valid_adjacent_loc(index_stamp, pre_word_index[-1]):
                        new_pre_word_index.append(list(index_stamp))
                        result.append(new_pre_word_index)
    return result


def valid_adjacent_loc(index_stamp, pre_index_stamp):
    if abs(index_stamp[0] - pre_index_stamp[0]) <= 1 and abs(index_stamp[1] - pre_index_stamp[1]) <= 1:
        return True
    return False


def permutations(string):
    result = set()
    str_list = [letter for letter in string]
    for i in itertools.permutations(str_list, len(str_list)):
        result_str = "".join(list(i))
        result.add(result_str)
    return list(result)

import Levenshtein
class Dictionary:
    def __init__(self,words):
        self.words=words

    def find_most_similar(self,term):
        # your code here
        min_distance = 999
        similiar_word = ""
        for compare_word in self.words:
            distance = self.calc_distance(compare_word, term)
            if distance < min_distance:
                min_distance = distance
                similiar_word = compare_word
        return similiar_word

    def calc_distance(self, compare_word, term):
        total_num = len(compare_word) * len(term)
        distance_matrix = np.zeros(total_num)
        distance_matrix = distance_matrix.reshape(len(compare_word), len(term))
        distance_matrix[:,0] = range(len(compare_word))
        distance_matrix[0, :] = range(len(term))
        for i in range(1, len(compare_word)):
            for j in range(1, len(term)):
                if compare_word[i] != term[j]:
                    distance_matrix[i, j] = min(distance_matrix[i-1, j], distance_matrix[i, j-1], distance_matrix[i-1, j-1]) + 1
                else:
                    distance_matrix[i, j] = min(distance_matrix[i-1, j] + 1, distance_matrix[i, j-1] + 1, distance_matrix[i-1, j-1])
        return distance_matrix[len(compare_word)-1, len(term)-1]


if __name__ == '__main__':
    words = ['cherry', 'peach', 'pineapple', 'melon', 'strawberry', 'raspberry', 'apple', 'coconut', 'banana']
    test_dict = Dictionary(words)
    result = test_dict.find_most_similar('aple')
    #result = test_dict.calc_distance('pineapple', 'aple')
    print result
