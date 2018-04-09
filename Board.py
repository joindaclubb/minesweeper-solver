from random import randint


class Board:
    def __init__(self, size):
        self.size = size
        self.matrix = [[0 for x in range(self.size)]
                      for y in range(self.size)]
        self.clicked = [[0 for x in range(self.size)]
                      for y in range(self.size)]
        self.known = [[None for x in range(self.size)]
                      for y in range(self.size)]
        self.flags = set()
        self.mines = set()
        
    def setup(self, toAdd = None):
        if toAdd == None:
            toAdd = self.size * 4 // 1
        while toAdd:
            i = randint(0, self.size - 1)
            j = randint(0, self.size - 1)
            if self.matrix[i][j] != -1:
                self.matrix[i][j] = -1
                self.mines.add((i,j))
                toAdd -= 1
                for a in [i - 1, i, i + 1]:
                    for b in [j - 1, j, j + 1]:
                        if a not in range(self.size) or b not in range(self.size):
                            continue
                        if self.matrix[a][b] != -1:
                            self.matrix[a][b] += 1
                            
    def get(self, x, y):
        return self.matrix[x][y]
    
    def click(self, i, j):
        self.clicked[i][j] = 1

    def flag(self, i, j):
        self.clicked[i][j] = 2
        self.flags.add((i,j))

    def unFlag(self, i, j):
        self.clicked[i][j] = 0
        self.flags.remove((i,j))

    def isFlagged(self, i, j):
        return self.clicked[i][j] == 2

    def wasClicked(self, i, j):
        return self.clicked[i][j] == 1

    def isWin(self):
        return self.mines == self.flags

    def getKnown(self, i, j):
        return self.known[i][j]

    def getLinearCoord(self, i, j):
        return j * self.size + i

    def getPairCoord(self, num):
        return (num % self.size, num // self.size)

    def getHiddenAdjacentMines(self, i, j):
        adjacentMines = self.getKnown(i,j)
        if adjacentMines == None:
            return -1
        for a in [i - 1, i , i + 1]:
            for b in [j - 1, j , j + 1]:
                if a not in range(self.size) or b not in range(self.size):
                    continue
                if self.isFlagged(a,b):
                    adjacentMines -= 1
        return adjacentMines

    def getSolvingEquations(self): # ((tile_x, tile_y, [ open adjacents ], hidden mines)
        borderTiles = []
        for i,j in [(i,j) for i in range(self.size) for j in range(self.size)]:
            unknowns = self.getNearbyUnknowns(i,j)
            if unknowns[0] and unknowns not in borderTiles:
                borderTiles += [unknowns]
        return borderTiles

    def getNearbyUnknowns(self, i, j):
        if not self.wasClicked(i,j):
            return (None,None)
        nearbys = []
        nearbyMines = self.get(i,j)
        for a,b in [(a,b) for a in [i - 1 , i , i + 1] for b in [j - 1 , j , j + 1]
                    if a in range(self.size) and b in range(self.size)]:
            if self.isFlagged(a,b):
                nearbyMines -= 1
            elif self.known[a][b] == None: 
                nearbys += [(a,b)]
        return (nearbys, nearbyMines)
