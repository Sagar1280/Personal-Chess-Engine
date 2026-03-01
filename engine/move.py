class Move:
    def __init__ (self,start_row,start_column,end_row,end_column,promotion = None):
        self.start_row = start_row
        self.start_column = start_column
        self.end_row = end_row
        self.end_column = end_column
        self.promotion = promotion
    
    def __repr__(self):
        return f"({self.start_row},{self.start_column}) -> ({self.end_row},{self.end_column})"