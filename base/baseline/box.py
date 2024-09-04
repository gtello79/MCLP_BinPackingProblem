class box:

    ## Constructor

    def __init__(self, id, large, width, heigth, rotx , roty, rotz):
        self.id = id
        self.l = large
        self.w = width
        self.h = heigth
        self.vol = large*heigth*width
        self.rotx = rotx
        self.roty = roty
        self.rotz = rotz

        self.calculateComplex()
    
    def calculateComplex(self):
        expo = 1
        self.complex = ((((self.l/self.h)*(self.l/self.w)*(self.w/self.h)))**expo) * self.vol
