from colorama import Fore, Style, init 

init(autoreset=True)

class Board:
    def __init__(self, emoji=True):
        self.emoji = emoji
        self.cells = [None] * 9

    def symbol(self, v):
        if v == "X":
            return Fore.RED + ("❌" if self.emoji else Fore.RED + "X")
        
        if v == "O":
            return Fore.BLUE + ("⭕" if self.emoji else Fore.BLUE + "O")
        
        return ""
    

    def render(self):
        s = [self.symbol(v) for v in self.cells]
        print(f"""
        {s[0]} | {s[1]} | {s[2]}
-----------
        {s[3]} | {s[4]} | {s[5]}
-----------
      {s[6]} | {s[7]} | {s[8]}
    """)

    def place(self, pos, player):
        try:
            pos = int(pos)
            if self.cells[pos] is None:
                self.cells[pos] = player 
                return True
        except:
            pass
        return False

    def free_cells(self):
        return [i for i, v in enumerate(self.cells) if v is None]
    
    def winner(self):
        combos = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  
            (0, 4, 8), (2, 4, 6)
        ]
        for a, b, c in combos:
            if self.cells[a] and self.cells[a] == self.cells[b] == self.cells[c]:
                return self.cells[a]
            return None 


    def full(self):
        return all(self.cells)


                      