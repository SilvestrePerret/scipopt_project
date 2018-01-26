import string

from constraint_programming import constraint_programming


def read_inputs(n):
    """
    read inputs

    :param n : integer in [1, 2], tells which crossword game to solve
    :return grid (list of list): [['#', '#', '#', '#', '#'], ['#', '#', '.', '#', '#']]
    : return words : ['to', 'at', 'tea', 'eat']
    """
    grid = [[]]
    with open("./crossword_problem/crossword%s.txt" % str(n), "r") as crossword_file:
        grid = list(map(list, crossword_file.read().split("\n")))

    with open("./crossword_problem/words%s.txt" % str(n), "r") as words_file:
        words = words_file.read().split("\n")

    return grid, words

def find_segments(case, cases):
    """
    Function which find zero, one or two segments for the case (input)
    """
    i, j = case

    same_row_cases = sorted([case for case in cases if case[0] == i], key=lambda x: abs(x[1]-j))
    row_seg = {case}
    for same_row_case in same_row_cases:
        if same_row_case[1]+1 in {case[1] for case in row_seg} or   \
                same_row_case[1]-1 in {case[1] for case in row_seg}:
            row_seg.add(same_row_case)

    same_col_cases = sorted([case for case in cases if case[1] == j], key=lambda x: abs(x[0]-i))
    col_seg = {case}
    for same_col_case in same_col_cases:
        if same_col_case[0]+1 in {case[0] for case in col_seg} or   \
                same_col_case[0]-1 in {case[0] for case in col_seg}:
            col_seg.add(same_col_case)

    segments = []
    if len(row_seg) > 1:
        segments.append(tuple(sorted(row_seg, key=lambda x: x[1])))
    if len(col_seg) > 1:
        segments.append(tuple(sorted(col_seg, key=lambda x: x[0])))

    return segments

def create_letter_word_set(case, cases, words):
    first_seg_set = set()

    segments = find_segments(case, cases)
    assert len(segments) >= 1

    seg = segments[0]
    for k, word in enumerate(words):
        if len(word) == len(seg):
            first_seg_set.add((word[seg.index(case)], k))

    if len(segments) == 1: # case n'est pas une intersection
        return first_seg_set

    assert len(segments) == 2 # case est une intersection
    second_seg_set = set()
    seg = segments[1]
    for k, word in enumerate(words):
        if len(word) == len(seg):
            second_seg_set.add((word[seg.index(case)], k))

    first_letter_set = {letter for letter, word in first_seg_set}
    second_letter_set = {letter for letter, word in second_seg_set}

    letters_set = first_letter_set.intersection(second_letter_set)

    first_seg_set = {(letter, word) for (letter, word) in first_seg_set if letter in letters_set}
    second_seg_set = {(letter, word) for (letter, word) in second_seg_set if letter in letters_set}

    return first_seg_set.union(second_seg_set)

def main(n):
    grid, words = read_inputs(n)

    # cases = {(1, 2), (2, 1), (2, 2), (2, 3), (3, 2)} par exemple
    cases = {(i, j) for i, row in enumerate(grid) for j, x in enumerate(row) if x == '.'}

    # segments = [((1,2),(2,2),(3,2)),((2,1),(2,2),(2,3))] par exemple
    segments = []
    for case in cases:
        for seg in find_segments(case, cases):
            if not seg in segments:
                segments.append(seg)

    # Modèle : les variables sont : cases + segments
    var = {}
    for case in cases:
        var[case] = set(string.ascii_letters)
    for seg in segments:
        var[seg] = {word for word in words if len(seg) == len(word)}

    # Solver instaciation
    P = constraint_programming(var)

    # Relations
    for seg in segments:
        for i, case in enumerate(seg):
            word_letter_set = set()
            for word in var[seg]:
                word_letter_set.add((word, word[i]))
            P.addConstraint(seg, case, word_letter_set)

    # Résultats
    print("Let solve it !")
    P.maintain_arc_consistency()
    dic_solve = P.solve()

    if dic_solve is None:
        print("No solution was found.")
        return

    for var, value in dic_solve.items():
        if len(var) == 2 and value in set(string.ascii_letters):
            i, j = var
            grid[i][j] = value

    for row in grid:
        for c in row:
            print(c, end='')
        print()
    
    for var, value in dic_solve.items():
        if not value in set(string.ascii_letters):
            print(value, var)


if __name__ == '__main__':
    main(2)