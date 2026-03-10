class Move:
    def __init__ (self,start_row,start_column,end_row,end_column,promotion = None):
        self.start_row = start_row
        self.start_column = start_column
        self.end_row = end_row
        self.end_column = end_column

        self.promotion = promotion 

        self.score = 0
    
    def __repr__(self):
        if self.promotion:
            return f"({self.start_row},{self.start_column}) -> ({self.end_row},{self.end_column}) = {self.promotion}"
        return f"({self.start_row},{self.start_column}) -> ({self.end_row},{self.end_column})"