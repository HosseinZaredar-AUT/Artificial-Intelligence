def read_file(file_path):
    f = open(file_path)
    n = int(f.readline())
    m = int(f.readline())
    i, j = map(int, f.readline().split())
    k = int(f.readline())
    red_mushrooms = []
    for _ in range(k):
        red_mushrooms.append(tuple(map(int, f.readline().split())))
    blue_mushrooms = []
    for _ in range(k):
        blue_mushrooms.append(tuple(map(int, f.readline().split())))
    blocks = []
    for line in f:
        blocks.append(tuple(map(int, line.split())))

    return i, j, n, m, blocks, red_mushrooms, blue_mushrooms


def h(state, red_mushrooms, blue_mushrooms):  # heuristic function

    # h = 0: DFS
    # return 0

    # h = manhattan distance from the nearest mushroom
    min_dist = 1000000
    for m in red_mushrooms:
        dist = abs(state['x'] - m[0]) + abs(state['y'] - m[1])
        if dist < min_dist:
            min_dist = dist
    for m in blue_mushrooms:
        dist = abs(state['x'] - m[0]) + abs(state['y'] - m[1])
        if dist < min_dist:
            min_dist = dist
    return min_dist


def lrta_star_cost(s, sp, H, red_mushrooms, blue_mushrooms):  # cost function
    if sp is None:
        return h(s, red_mushrooms, blue_mushrooms)
    else:
        return 1 + H[(sp['x'], sp['y'])]


def actions(state, n, m):  # returns all possible actions in the given state
    possible_actions = []
    if state['y'] != 1:
        possible_actions.append('DOWN')
    if state['y'] != n:
        possible_actions.append('UP')
    if state['x'] != 1:
        possible_actions.append('LEFT')
    if state['x'] != m:
        possible_actions.append('RIGHT')
    return possible_actions


def do_action(state, action, blocks):  # does the action and returns the new state
    if action == 'DOWN':
        if (state['x'], state['y'] - 1) in blocks:
            return {'x': state['x'], 'y': state['y']}
        else:
            return {'x': state['x'], 'y': state['y'] - 1}

    elif action == 'UP':
        if (state['x'], state['y'] + 1) in blocks:
            return {'x': state['x'], 'y': state['y']}
        else:
            return {'x': state['x'], 'y': state['y'] + 1}

    elif action == 'LEFT':
        if (state['x'] - 1, state['y']) in blocks:
            return {'x': state['x'], 'y': state['y']}
        else:
            return {'x': state['x'] - 1, 'y': state['y']}

    elif action == 'RIGHT':
        if (state['x'] + 1, state['y']) in blocks:
            return {'x': state['x'], 'y': state['y']}
        else:
            return {'x': state['x'] + 1, 'y': state['y']}


def lrta_star(initial_state, n, m, blocks, red_mushrooms, blue_mushrooms):  # LRTA* Algorithm
    eaten_red_mushrooms = 0
    eaten_blue_mushrooms = 0
    step = 1

    H = dict()
    result = dict()

    a = None
    s = None
    sp = initial_state

    while True:

        step_str = '0' + str(step) if step < 10 else step
        print(f'Step {step_str}: In ({sp["x"], sp["y"]})', end=', ')

        # calculating heuristic if we've never been in this state before
        if (sp['x'], sp['y']) not in H:
            H[(sp['x'], sp['y'])] = h(sp, red_mushrooms, blue_mushrooms)

        # updating parents heuristic
        if s is not None:
            result[(s['x'], s['y'], a)] = sp
            min_cost = 1000000
            for b in actions(s, n, m):
                cost = lrta_star_cost(s, result.get((s['x'], s['y'], b)), H, red_mushrooms, blue_mushrooms)
                if cost < min_cost:
                    min_cost = cost
            H[(s['x'], s['y'])] = min_cost
            print(f'H({s["x"], s["y"]}) <- {min_cost}', end=', ')

        # finding the best action
        min_cost = 1000000
        best_action = ''
        for b in actions(sp, n, m):
            cost = lrta_star_cost(sp, result.get((sp['x'], sp['y'], b)), H, red_mushrooms, blue_mushrooms)
            if cost < min_cost:
                min_cost = cost
                best_action = b

        print(f'Go {best_action}', end='')

        # taking the actions
        a = best_action
        s = sp
        sp = do_action(sp, best_action, blocks)

        # dealing with the result
        if (sp['x'], sp['y']) in red_mushrooms:
            red_mushrooms.remove((sp['x'], sp['y']))
            eaten_red_mushrooms += 1
            print(', Eat the red mushroom!', end='')

        if (sp['x'], sp['y']) in blue_mushrooms:
            blue_mushrooms.remove((sp['x'], sp['y']))
            eaten_blue_mushrooms += 1
            print(', Eat the blue mushroom!', end='')

        print()
        if eaten_red_mushrooms > 0 and eaten_blue_mushrooms > 0:
            break

        step += 1


def main():

    # reading the input file
    i, j, n, m, blocks, red_mushrooms, blue_mushrooms = read_file('Mario.txt')
    initial_state = {'x': i, 'y': j}

    # solving the problem
    lrta_star(initial_state, n, m, blocks, red_mushrooms, blue_mushrooms)


if __name__ == '__main__':
    main()
