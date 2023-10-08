a = [1, 1, 1, 2, 8, 6, 1]
b = [2, 4, 6, 1, 4, 18, 61]
c = [2, 8, 18, 2, 1, 1, 8]


def printThreeArrays(a: list, b: list, c: list):
    listOfUniqueValues = []

    if len(a) != len(b) or len(a) != len(c):
        raise ValueError("These lists should be the same length")
    print(*('a', 'b', 'c'), sep='\t')
    for values in zip(a, b, c):
        originValue = tuple(sorted(values))
        if not originValue in listOfUniqueValues:
            listOfUniqueValues.append(originValue)
            print(*values, sep='\t')

printThreeArrays(a,b,c)