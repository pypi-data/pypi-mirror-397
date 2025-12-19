class SelectionPoint(ObservableStruct):
    def __init__(self, x, y, r, color):
        self.x = x
        self.y = y
        self.r = r
        self.color = color
        self.show_in_map = True
        self.show_in_plot = True
class SelectionReference(ObservableStruct):
    def __init__(self, x, y, r, color):
        self.x = x
        self.y = y
        self.r = r
        self.color = color
        self.show_in_map = True
class SelectionProfile(ObservableStruct):
    def __init__(self, x0, y0, x1, y1, r, color):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.r = r
        self.color = color
        self.show_in_map = True
        
class Selections(ObservableStruct):
    def __init__(self):
        self.points     = ObservableList()
        self.references = ObservableList()
        self.profiles   = ObservableList()

class Project(ObservableStruct):
    def __init__(self):
        self.layers = ObservableList()
        self.selections = Selections()
        self.reference_band = IndexInto(self.selections.references)

