import random 

class AI:
    def __init__(self,  board, level="easy"):
        self.board = board
        self.level = level 

    
    def move(self):
        if self.level == "hard":
            return self.minimax(True)[1]
        return random.choice(self.board.free_cells())


    def minimax(self, is_max):
        winner = self.board.winner()
        if winner == "O":
            return (1, None)
        if winner == "X":
            return (-1, None)

        if self.board.full():
            return (0, None)


        best = (-999, None) if is_max else (999, None)

        for cell in self.board.free_cells():
            self.board.cells[cell] = "O" if is_max else "X"
            score = self.minimax(not is_max)[0]
            self.board.cells[cell] = None 


            if is_max and score > best[0]:
                best = (score, cell)
            if not is_max and score < best[0]:
                best = (score, cell)

            return best