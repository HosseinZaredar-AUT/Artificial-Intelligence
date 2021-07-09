import re
import copy
import heapq
from itertools import permutations


class Node:  # a class, representing nodes of the state space tree
    def __init__(self, parent, action, cost, state, jafar):
        self.parent = parent
        self.action = action
        self.cost = cost
        self.state = state
        self.jafar = jafar

    def __lt__(self, other):
        return True


def heuristic(node):  # heuristic function
    # 1: h(node) = 0, =BFS
    # return 0

    # 2: simple horizontal distance
    global goal_rows
    global class_dict
    global jafars_class
    global m

    state = node.state
    sigma = 0

    # going through all rows
    for i in range(len(state)):
        # going through all students in the row
        for j in range(len(state[0])):
            student = state[i][j]
            if student == '#':
                continue
            min_distance = m + 1
            student_class = goal_rows[class_dict[student[1]]]

            # calculating the horizontal distance of student to the place he's supposed to be
            # (jafar is ignored)
            for k in range(len(student_class)):
                if student == student_class[k]:
                    final_location = k
                    if student[1] == jafars_class:
                        final_location += 1
                    distance = int(abs(j - final_location))
                    if distance < min_distance:
                        min_distance = distance
            sigma += min_distance
    return sigma

    # 3: min (manhattan distance) for all goal states


def a_star_search(priority_queue):  # A* algorithm

    # accessing the global variables
    global hashed_goal_states

    all_expanded_set = set()  # all expanded, is only used to prevent duplicate addition of nodes priority queue
    explored_num = 0  # total number of nodes explored
    expanded_num = 0  # total number of nodes expanded

    while True:

        # checking if the priority queue is empty which means there's no solution
        if len(priority_queue) == 0:
            print('No Solution!')
            return

        # popping a node
        priority, node = heapq.heappop(priority_queue)

        # creating hashed state
        all_rows = []
        for r in node.state:
            for c in r:
                all_rows.append(c)

        hashed_state = tuple(all_rows).__hash__()

        explored_num += 1  # one node explored

        # checking if it is a goal state
        if hashed_state in hashed_goal_states:
            # producing the path and printing the proper outputs
            path = []
            current = node
            while current.parent is not None:
                path.insert(0, current.action)
                current = current.parent
            print('Depth:', len(path))
            print('Path:', path)
            print('#Expanded:', expanded_num)
            print('#Explored:', explored_num)
            print('Final State:')
            for r in node.state:
                print(r)
            return

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
            new_node = Node(node, actions[i][2], node.cost + 1, new_state, new_jafar)

            # creating child's hashed node
            all_rows = []
            for r in new_state:
                for c in r:
                    all_rows.append(c)
            all_rows.append(new_node.cost)
            child_hashed_node = tuple(all_rows).__hash__()

            # checking if the child node is not already in all_expanded_set
            if child_hashed_node in all_expanded_set:
                continue

            # adding the child node to all_expanded_set
            all_expanded_set.add(child_hashed_node)

            # adding the new_node to priority_queue i.e. actual frontier list
            heapq.heappush(priority_queue, (heuristic(new_node) + new_node.cost, new_node))

            expanded_num += 1  # one node expanded


# -------------------- beginning of the program --------------------
n, m = map(int, input().split())

# creating the rows matrix
class_names = set()
matrix = []
all_students = []
initial_jafar = None
for i in range(n):
    students = input().split()
    row = []
    for j in range(len(students)):
        if students[j] == '#':
            initial_jafar = (i, j)
            jafars_class = i
            row.append('#')
        else:
            lst = re.split('([a-z])', students[j])
            lst.pop()
            row.append((int(lst[0]), lst[1]))
            all_students.append((int(lst[0]), lst[1]))
            class_names.add(lst[1])

    matrix.append(row)

# creating goal rows (used in heuristic function)
class_names = list(class_names)
goal_rows = [[] for i in range(n)]
class_dict = {}
for i in range(len(class_names)):
    class_dict[class_names[i]] = i

for s in all_students:
    goal_rows[class_dict[s[1]]].append(s)

for i in range(n):
    goal_rows[i].sort(key=lambda x: x[0], reverse=True)

for i in range(n):
    if len(goal_rows[i]) == m - 1:
        goal_rows[i].insert(0, '#')


# creating all possible goal states (used to check if the solution is found)
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


# creating the initial node
initial_node = Node(None, None, 0, matrix, initial_jafar)
pq = []
heapq.heappush(pq, (heuristic(initial_node) + initial_node.cost, initial_node))

# running the algorithm
a_star_search(pq)
