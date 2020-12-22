class bin:
    def __init__(self, boxes):
        self.boxes = boxes
        self.

    def getMostComplex(self):
        idBox = None
        eval = 0
        for b in self.boxes:
            if(idBox is None):
                idBox = b.idBox
            else:
                if(b.complex > eval):
                    idBox = b.idBox
                    eval = b.complex
        return idBox, eval    

    def getBox(self, idBox):
        for b in self.boxes:
            if (idBox == b.idBox):
                return b 
            else:
                continue   

    def getAllIndex(self):
        idBoxes = [ b.idBox for b in self.boxes ]
        return idBoxes