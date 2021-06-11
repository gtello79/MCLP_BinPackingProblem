class box:
    def __init__(self, dim, id):
        self.idBox = id
        self.x, self.y, self.z = dim
        self.vol = x*y*z
        self.complex = None
        
    def __init__(self, id, l, w, h, rotx, roty, rotz):
        self.id = id
        self.l = l; self.w = w; self.h = h;
        self.rotx = rotx; self.roty = roty; self.rotz = rotz;
    
    def calculateComplex(self):
        expo = 1
        self.complex = ((((self.x/self.z)*(self.x/self.y)*(self.y/self.z)))**expo) * self.vol
        
