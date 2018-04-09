from tkinter import *
from random import randint
from heapq import heappush, heappop
from sympy import Matrix, solve
from Board import *

scale = 20
DEBUG = 1
BACKGROUND = "gray"
MINECOLOR = "red"
INCLUDE_LINES = 1

colors = {
    -1 : "black",
    0 : "snow",
    1 : "sky blue",
    2 : "blue",
    3 : "green",
    4 : "yellow",
    5 : "orange",
    6 : "dark orange",
    7 : "dark orange",
    8 : "dark orange"
    }

def debug(*args):
    if not DEBUG:
        return
    string = ""
    for arg in args:
        string += str(arg)
    print(string)

class Main:
    def __init__(self, size):
        self.added = []
        self.size = size
        self.game_over = 0
        
        self.master = Tk()
        self.master.title("Minesweeper Solver")
        
        self.board = Board(self.size)
        self.board.setup()
        
        self.makeWidgets()

        self.master.bind("h", self.hintCommand)
        self.master.bind("n", self.newCommand)
        self.master.bind("s", self.stepCommand)
        self.master.bind("r", self.executeCommand)
        self.master.bind("q", lambda event: self.master.destroy())
        self.master.bind("u", self.restartCommand)
        self.master.bind("g", self.guessCommand)
        self.master.bind("c", self.cheatCommand)


    def makeWidgets(self):
        self.canvas = Canvas(self.master,
                             height = self.size * scale,
                             width  = self.size * scale,
                             bg = BACKGROUND)
        
        self.canvas.bind("<Button-1>", self.handleHumanLeft)
        self.canvas.bind("<Button-3>", self.handleHumanRight)
        
        if INCLUDE_LINES:
            for i in range(self.size):
                self.canvas.create_line(scale * i, 0, scale * i, self.size * scale)
                self.canvas.create_line(0, scale * i, self.size * scale, scale * i)
        self.canvas.pack()
        
    def handleHumanLeft(self, event):
        self.doLeftClick(event.x // scale, event.y // scale)

    def handleHumanRight(self, event):
        self.doRightClick(event.x // scale, event.y // scale)

    def doLeftClick(self, i, j):
        if not self.board.wasClicked(i, j):
            self.board.click(i,j)
            if self.board.matrix[i][j] == 0:
                self.bigReveal(i,j)
            else:
                self.doTileTick(i,j)
            
    def doRightClick(self, i, j):
        if not self.board.wasClicked(i, j) == 1:
            if self.board.isFlagged(i, j):
                self.canvas.delete(str(i * scale) + "," + str(j * scale))
                self.canvas.create_rectangle(i * scale, j * scale, i * scale + scale, j * scale + scale, fill = BACKGROUND)
                self.board.unFlag(i, j)
            else:
                self.board.flag(i, j)
                self.canvas.create_rectangle(i * scale, j * scale, i * scale + scale, j * scale + scale, fill = MINECOLOR)
                if self.board.isWin():
                    self.end()
    
    def doTileTick(self, i, j):
        value = self.board.get(i, j)
        if value == -1:
            debug("Hit mine at ", i, ", ", j)
            self.end(False)
        self.canvas.create_rectangle(i * scale, j * scale, i * scale + scale, j * scale + scale, fill = colors[self.board.get(i, j)])
        if value != 0:
            self.canvas.create_text(i * scale + scale / 2, j * scale + scale / 2, text = str(value))
        self.board.known[i][j] = value
        return value

    def bigReveal(self, i, j):
        queue = Queue()
        queue.add((i,j))
        while not queue.isEmpty():
            x,y = queue.get()
            if self.board.matrix[x][y] > 0 and not self.board.wasClicked(x,y):
                self.doTileTick(x, y)
                self.board.click(x,y)
            if not self.board.get(x,y):
                self.doTileTick(x , y)
                self.board.click(x,y)
                for a in [x - 1, x , x + 1]:
                    for b in [y - 1, y , y + 1]:
                        if a in range(self.size) and b in range(self.size) and (a,b) not in self.added:
                            self.added.append((a,b))
                            queue.add((a,b))
                            
    def hintCommand(self, event):
        for i in range(self.size):
            for j in range(self.size):
                if self.board.get(i,j) == 0 and not self.board.wasClicked(i,j):
                    self.bigReveal(i,j)
                    return

    def restartCommand(self, event):
        matrix = self.board.matrix
        size = self.size
        self.master.destroy()
        self.__init__(size)
        self.board.matrix = matrix

    def newCommand(self, event):
        size = self.size
        self.master.destroy()
        self.__init__(size)

    def cheatCommand(self, event):
        i = event.x // scale
        j = event.y // scale
        if self.board.wasClicked(i,j):
            return
        elif self.board.get(i,j) == -1:
            self.doRightClick(i,j)
        else:
            self.doLeftClick(i,j)

    def stepCommand(self, event):
        if not self.game_over:
            self.solveWithAlgebra(True)

    def executeCommand(self, event):
        canDoStuff = True
        count = 1
        while canDoStuff and not self.game_over:
            debug("Stepped " + str(count) + " times")
            canDoStuff= self.solveWithAlgebra(False)
            count += 1

    
    def guessCommand(self, event):
        print("Not implemented!")

    def solveWithAlgebra(self, singleStep = False):
        matrix_A = []
        matrix_b = []
        didWork = False

        # MAKE ALL EASY MOVES TO REDUCE LOAD ON LA SECTION #
        easyWork = True
        while easyWork and not self.game_over:
            solvingEquations = [([self.board.getLinearCoord(c[0],c[1])
                              for c in coords], numMines)
                            for coords, numMines in self.board.getSolvingEquations()]
            easyWork = self.checkForEasyMoves(solvingEquations, singleStep)
            if easyWork and singleStep:
                return
        if self.game_over:
            return
    
        # HARDER LINEAR ALGEBRA STUFF #
        for equation in solvingEquations:
            line = [0 for i in range(self.size * self.size)]
            for var in equation[0]:
                line[var] = 1
            matrix_A += [line]
            matrix_b += [equation[1]]

        matrix_A = Matrix(matrix_A)
        matrix_b = Matrix(matrix_b)

        solution = matrix_A.gauss_jordan_solve(matrix_b)

        num = 0
        for variable in solution[0]:
            i,j = self.board.getPairCoord(num)
            if variable in [0,1]:
                if variable == 1:
                    self.doRightClick(i,j)
                    if singleStep:
                        return
                elif variable == 0:
                    self.doLeftClick(i,j)
                    if singleStep:
                        return
                didWork = True
                

            num += 1

        return didWork

    def checkForEasyMoves(self,equations, singleMove = False): # Naive solution
        work = False
        for coordinates, numMines in equations:
            if len(coordinates) == numMines:
                for coord in coordinates:
                    i,j = self.board.getPairCoord(coord)
                    if not self.board.isFlagged(i,j):
                        self.doRightClick(i,j)
                        if singleMove:
                            return True
                work = True
            elif numMines == 0:
                for coord in coordinates:
                    i,j = self.board.getPairCoord(coord)
                    self.doLeftClick(i,j)
                    if singleMove:
                        return True
                work = True
            
        return work
            
            
                    
                
    def end(self, win = True):
        if win:
            print("Win!")
            for i,j in [(i,j) for i in range(self.size) for j in range(self.size)]:
                if not self.board.wasClicked(i,j) and not self.board.isFlagged(i,j):
                    self.doLeftClick(i,j)
        else:
            print("Loss!")
        
        self.game_over = 1
                    
                        


class Queue:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items += [item]

    def get(self):
        return self.items.pop()

    def isEmpty(self):
        return self.items == []

main = Main(35)
main.master.mainloop()
