from numpy.lib.function_base import _calculate_shapes


class bin:
    def __init__(self, id, boxes, utilization):
        self.id = id
        self.boxes = boxes
        self.utilization = utilization
        self.verify = True


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

    def __str__ (self) -> str:
        boxes_list = ''
        for box in self.boxes.keys():
            boxes_list = boxes_list + str([box.id, self.boxes[box]]) + ", "
        return boxes_list