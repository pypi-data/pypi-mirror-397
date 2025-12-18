from .board import Board
from .ai import AI

class TicTacToe:
    def __init__(self, ai=None, emoji=True):
        self.board = Board(emoji=emoji)
        self.current_player = "X"
        self.ai = AI(self.board,  ai) if ai else None 


    def switch(self):
        self.current = "O" if self.current == "X" else "X"


    def play(self):
        while True:
            self.board.render()

            if self.ai and self.current == "O":
                move = self.ai.move()
            else:
                move = input(f"Player {self.current} (0-8):") 

            if not self.board.place(move, self.current):
                print("❌ Invalid move")
                continue

            winner = self.board.winner()
            if winner:
                self.board.render()
                print(f"🎉 Player {winner} wins!")
                return winner 


            if self.board.full():
                self.board.render()
                print("🤝 Draw!")
                return "draw"
            
            self.switch()