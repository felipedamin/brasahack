import random
numLin = 15
numCols = 15


def generateMap(lines, cols):
    matrix = []
    for n in range(lines):
        matrix.append([])
        for m in range(cols):
            matrix[n].append(1)
    return matrix

def generatePositons():
    cddX = random.randrange(5,8)
    cddY = random.randrange(5,8)

    cluster1X = random.randrange(1,5)
    cluster1Y = random.randrange(1,5)

    cluster2X = random.randrange(1,5)
    cluster2Y = random.randrange(8,14)

    cluster3X = random.randrange(1,5)
    cluster3Y = random.randrange(8,14)

    cluster4X = random.randrange(5,8)
    cluster4Y = random.randrange(1,3)

    cluster5X = random.randrange(11,14)
    cluster5Y = random.randrange(1,5)

    cluster6X = random.randrange(11,14)
    cluster6Y = random.randrange(6,10)

    cluster7X = random.randrange(6,10)
    cluster7Y = random.randrange(11,14)

    return {"cdd": (cddX, cddY), "bars": [(cluster1X, cluster1Y), (cluster2X, cluster2Y), (cluster3X, cluster3Y), (cluster4X, cluster4Y), (cluster5X, cluster5Y), (cluster6X, cluster6Y), (cluster7X, cluster7Y)]}

def populateMatrix(mapa, positions):
    for i in range(len(mapa)):
        for j in range(len(mapa[i])):
            if (i,j) == positions["cdd"]:
                mapa[i][j] = "C"
            elif (i,j) in positions["bars"]:
                mapa[i][j] = "B"
    return mapa

def main():
    mapa = generateMap(numLin, numCols)
    positions = generatePositons()
    populateMatrix(mapa, positions)

    return (mapa, positions)

main()