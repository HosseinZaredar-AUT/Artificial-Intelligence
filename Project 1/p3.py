import re
import copy
from itertools import permutations
from _collections import OrderedDict


class Node:  # a class, representing nodes of the state space
    def __init__(self, parent, action, cost, state, jafar):
        self.parent = parent
        self.action = action
        self.cost = cost
        self.state = state
        self.jafar = jafar

    def __lt__(self, other):
        return True


def print_results(path, goal_node):  # printing the proper outputs
    # accessing the global variables
    global expanded_num
    global explored_num
    global initial_node

    print('Depth:', len(path))
    print('Path:', path)
    print('#Expanded:', expanded_num)
    print('#Explored:', explored_num)
    print('Final State:')
    for r in goal_node.state:
        print(r)


def is_found(g_frontier_dict, s_frontier_dict):  # checks if there's any common state in given frontier dictionaries

    # checking if s_frontier_dict and g_frontier_dict have anything in common
    hashed_common_state = None
    for i in s_frontier_dict:
        if i in g_frontier_dict:
            hashed_common_state = i
            break

    # if any state if found
    if hashed_common_state is not None:
        g_final_node = g_frontier_dict[hashed_common_state]
        s_final_node = s_frontier_dict[hashed_common_state]

        print(s_final_node.state)

        # creating the path
        path = []

        # forward
        current = s_final_node
        while current.parent is not None:
            path.insert(0, current.action)
            current = current.parent

        # backward
        current = g_final_node
        reverse_dict = {'up': 'down', 'down': 'up', 'right': 'left', 'left': 'right'}
        while current.parent is not None:
            path.append(reverse_dict[current.action])
            current = current.parent

        return True, path, current

    else:
        return False, '', ''


def one_step_bfs(frontier_dict, explored_set, depth):  # exploring nodes with in the given depth

    # accessing global variables
    global explored_num
    global expanded_num

    while True:
        if len(frontier_dict) == 0:
            return

        # getting the node at the front of the queue
        hashed_state = next(iter(frontier_dict))
        node = frontier_dict[hashed_state]

        # if it's depth is bigger that want is supposed to be explored, we're done
        if node.cost != depth:
            return

        explored_num += 1

        # adding node's state to explored_set
        explored_set.add(hashed_state)

        # popping the node's state from frontier_dict
        frontier_dict.pop(hashed_state)

        # producing the 4 moves
        actions = [
            [0, 1, 'right'],
            [1, 0, 'down'],
            [-1, 0, 'up'],
            [0, -1, 'left']
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

            # creating a hashed state
            all_rows = []
            for r in new_state:
                for c in r:
                    all_rows.append(c)
            child_hashed_state = tuple(all_rows).__hash__()

            # checking if child's state is not already expanded or explored
            if child_hashed_state in explored_set or child_hashed_state in frontier_dict:
                continue

            # adding the child node to the queue
            new_node = Node(node, actions[i][2], node.cost + 1, new_state, new_jafar)
            frontier_dict[child_hashed_state] = new_node
            expanded_num += 1


def bidirectional_bfs(source_node, goal_nodes):  # bidirectional BFS algorithm

    # accessing global variables
    global explored_num
    global expanded_num

    # explored sets
    s_explored_set = set()
    g_explored_set = set()

    # frontier ordered dictionaries
    s_frontier_dict = OrderedDict()
    g_frontier_dict = OrderedDict()

    # creating initial node's hashed state
    all_rows = []
    for r in source_node.state:
        for c in r:
            all_rows.append(c)
    hashed_state = tuple(all_rows).__hash__()
    s_frontier_dict[hashed_state] = initial_node

    # creating goal nodes' hashed states
    for g in goal_nodes:
        all_rows = []
        for r in g.state:
            for c in r:
                all_rows.append(c)
        hashed_state = tuple(all_rows).__hash__()
        g_frontier_dict[hashed_state] = g

    # checking if solution is already found
    found, path, goal_node = is_found(g_frontier_dict, s_frontier_dict)
    if found:
        print_results(path, goal_node)
        return

    depth = 0
    while True:

        # checking if any of queues are empty which means there's no solution
        if len(s_frontier_dict) == 0 or len(g_frontier_dict) == 0:
            print('No Solution!')
            return

        # exploring one depth backward
        one_step_bfs(g_frontier_dict, g_explored_set, depth)

        # checking if solution is found
        found, path, goal_node = is_found(g_frontier_dict, s_frontier_dict)
        if found:
            print_results(path, goal_node)
            return

        # exploring one depth forward
        one_step_bfs(s_frontier_dict, s_explored_set, depth)

        # checking if solution is found
        found, path, goal_node = is_found(g_frontier_dict, s_frontier_dict)
        if found:
            print_results(path, goal_node)
            return

        depth += 1


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

initial_node = Node(None, None, 0, matrix, initial_jafar)

# creating all possible goal states
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

# creating goal nodes
goal_nodes = []
for i in range(len(goal_states)):
    state = goal_states[i]
    jafar_row = -1
    for j in range(n):
        if state[j][0] == '#':
            jafar_row = j
            break
    goal_nodes.append(Node(None, None, 0, state, (jafar_row, 0)))

expanded_num = 1  # total number of nodes expanded
explored_num = 0  # total number of nodes explored

bidirectional_bfs(initial_node, goal_nodes)
