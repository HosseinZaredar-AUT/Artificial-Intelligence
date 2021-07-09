import re
import copy
from _collections import OrderedDict
from itertools import permutations


class Node:  # a class, representing nodes of the state space
    def __init__(self, parent, action, cost, state, jafar):
        self.parent = parent
        self.action = action
        self.cost = cost
        self.state = state
        self.jafar = jafar


def print_result(final_node):  # printing the proper outputs
    # accessing the global variables
    global expanded_num
    global explored_num

    # producing the path and printing the proper outputs
    path = []
    current = final_node
    while current.parent is not None:
        path.insert(0, current.action)
        current = current.parent
    print('Depth:', len(path))
    print('Path:', path)
    print('#Expanded:', expanded_num)
    print('#Explored:', explored_num)
    print('Final State:')
    for r in final_node.state:
        print(r)


def depth_limit_search(frontier_dict, explored_dict):  # a stack-based, graph search, depth limit search algorithm
    # accessing the global variables
    global expanded_num
    global explored_num

    cutoff_occurred = False  # tracking if a cutoff is ever happened

    while True:
        # checking if the stack is empty
        if len(frontier_dict) == 0:
            break

        # removing a node to explore
        hashed_state, (node, limit) = frontier_dict.popitem()
        # print(node.state)

        # adding to explored
        explored_dict[hashed_state] = node

        explored_num += 1  # one node explored

        if hashed_state in hashed_goal_states:  # checking if it is a goal state
            return 'success', node
        elif limit == 0:  # checking if it exceeds the limit
            cutoff_occurred = True
            continue
        else:
            # producing the 4 moves
            actions = [
                [0, -1, 'left'],
                [1, 0, 'down'],
                [0, 1, 'right'],
                [-1, 0, 'up'],

            ]

            reverse_dict = {'up': 'down', 'down': 'up', 'right': 'left', 'left': 'right'}

            for i in range(4):  # checking every move

                # preventing parent node expanding for better performance
                if node.action is not None and reverse_dict[node.action] == actions[i][2]:
                    continue

                # checking if the action is possible i.e. it's not out of bounds
                if node.jafar[0] + actions[i][0] < 0 \
                        or node.jafar[1] + actions[i][1] < 0 \
                        or node.jafar[0] + actions[i][0] == len(node.state) \
                        or node.jafar[1] + actions[i][1] == len(node.state[0]):
                    continue

                # creating the new node
                new_state = copy.deepcopy(node.state)
                new_state[node.jafar[0]][node.jafar[1]] = \
                    new_state[node.jafar[0] + actions[i][0]][node.jafar[1] + actions[i][1]]
                new_state[node.jafar[0] + actions[i][0]][node.jafar[1] + actions[i][1]] = '#'
                new_jafar = (node.jafar[0] + actions[i][0], node.jafar[1] + actions[i][1])
                new_node = Node(node, actions[i][2], node.cost + 1, new_state, new_jafar)

                # calculating the hashed value of child's state
                child_all_rows = []
                for r in new_state:
                    for c in r:
                        child_all_rows.append(c)

                child_hashed_state = tuple(child_all_rows).__hash__()

                # checking if child's state is already explored
                if child_hashed_state in explored_dict:
                    existing_node = explored_dict[child_hashed_state]
                    if existing_node.cost <= new_node.cost:
                        continue

                # checking if child's state is already expanded
                if child_hashed_state in frontier_dict:
                    existing_node, existing_limit = frontier_dict[child_hashed_state]
                    if existing_node.cost <= new_node.cost:
                        continue

                frontier_dict[child_hashed_state] = (new_node, limit - 1)

                expanded_num += 1  # one node expanded

    # checking the results
    if cutoff_occurred:
        return 'cutoff', ''
    else:
        return 'failure', ''


def iterative_deepening_dfs(initial_state, jafar, initial_limit):  # iterative deepening DFS algorithm

    # accessing the global variables
    global expanded_num
    global explored_num

    # calculating the hashed value of initial state
    all_rows = []
    for r in initial_state:
        for c in r:
            all_rows.append(c)
    hashed_state = tuple(all_rows).__hash__()

    # creating the initial node
    initial_node = Node(None, None, 0, initial_state, jafar)

    limit = initial_limit  # starting from the initial limit
    while True:
        # print('limit = ', limit, ' ------------------------')

        explored_dict = {}  # explored dictionary, is used to prevent duplicate node exploration
        frontier_dict = OrderedDict()  # an ordered dictionary used as DFS stack
        expanded_num += 1

        # initializing the stack
        frontier_dict[hashed_state] = (initial_node, limit)

        # calling the depth limit search function for a certain limit
        result, final_node = depth_limit_search(frontier_dict, explored_dict)

        # dealing with the result
        if result == 'cutoff':  # if a cutoff happened
            limit += 1
        elif result == 'failure':  # if whole state space was searched but no solution was found
            print('No Solution!')
            return result
        else:  # if a solution was found
            print_result(final_node)
            return


# -------------------- beginning of the program --------------------
n, m = map(int, input().split())

# creating the rows matrix
matrix = []
class_names = set()
all_students = []
initial_jafar = None
for i in range(n):
    students = input().split()
    row = []
    for j in range(len(students)):
        if students[j] == '#':
            initial_jafar = (i, j)
            row.append('#')
        else:
            lst = re.split('([a-z])', students[j])
            lst.pop()
            row.append((int(lst[0]), lst[1]))
            all_students.append((int(lst[0]), lst[1]))
            class_names.add(lst[1])

    matrix.append(row)


# creating the goal states
class_names = list(class_names)
goal_rows = [[] for i in range(n)]
d = {}
for i in range(len(class_names)):
    d[class_names[i]] = i

for s in all_students:
    goal_rows[d[s[1]]].append(s)

for i in range(n):
    goal_rows[i].sort(key=lambda x: x[0], reverse=True)

for i in range(n):
    if len(goal_rows[i]) == m - 1:
        goal_rows[i].insert(0, '#')

goal_states = list(permutations(goal_rows))

for i in range(len(goal_states)):
    goal_states[i] = list(goal_states[i])

hashed_goal_states = set()
for g in goal_states:
    g_all_rows = []
    for row in g:
        for column in row:
            g_all_rows.append(column)
    g_hashed_state = tuple(g_all_rows).__hash__()
    hashed_goal_states.add(g_hashed_state)

explored_num = 0  # total number of nodes explored
expanded_num = 0  # total number of nodes expanded

init_limit = 1  # the initial limit
iterative_deepening_dfs(matrix, initial_jafar, init_limit)
