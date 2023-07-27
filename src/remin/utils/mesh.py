import numpy as np
from enum import IntEnum
from pyevtk.hl import unstructuredGridToVTK

class Gmsh(IntEnum):
    LIN_2   = 1
    TRI_3   = 2
    QUA_4   = 3
    TET_4   = 4
    HEX_8   = 5
    PRI_6   = 6
    PYR_5   = 7
    LIN_3   = 8
    TRI_6   = 9
    QUA_9   = 10
    TET_10  = 11
    HEX_27  = 12
    PRI_18  = 13
    PNT     = 15
    QUA_8   = 16
    HEX_20  = 17
    PRI_15  = 18

class VTK(IntEnum):
    LIN_2   = 3
    TRI_3   = 5
    QUA_4   = 9
    TET_4   = 10
    HEX_8   = 12
    PRI_6   = 13
    PYR_5   = 14
    LIN_3   = 21
    TRI_6   = 22
    QUA_9   = 28
    TET_10  = 24
    HEX_27  = 29
    PRI_18  = 32
    PNT     = 1
    QUA_8   = 23
    HEX_20  = 25
    PRI_15  = 26
    
class Mesh:

    def __init__(self) -> None:
        self.version = None
        self.elements = None
        self.vertices = [None] * 3   
        self.offsets = None
        self.elementTypes = None

    def writeVTK(self, fileName):
        vtkTypes = np.zeros_like(self.elementTypes)
        for i, elementType in enumerate(self.elementTypes):
            if elementType == Gmsh.LIN_2:
                vtkTypes[i] = VTK.LIN_2
            elif elementType == Gmsh.TRI_3:
                vtkTypes[i] = VTK.TRI_3
            elif elementType == Gmsh.QUA_4:
                vtkTypes[i] = VTK.QUA_4
            elif elementType == Gmsh.TET_4:
                vtkTypes[i] = VTK.TET_4
            elif elementType == Gmsh.HEX_8:
                vtkTypes[i] = VTK.HEX_8
            elif elementType == Gmsh.PYR_5:
                vtkTypes[i] = VTK.PYR_5
            elif elementType == Gmsh.PRI_6:
                vtkTypes[i] = VTK.PRI_6
            elif elementType == Gmsh.LIN_3:
                vtkTypes[i] = VTK.LIN_3
            elif elementType == Gmsh.TRI_6:
                vtkTypes[i] = VTK.TRI_6
            elif elementType == Gmsh.QUA_9:
                vtkTypes[i] = VTK.QUA_9
            elif elementType == Gmsh.TET_10:
                vtkTypes[i] = VTK.TET_10
            elif elementType == Gmsh.HEX_27:
                vtkTypes[i] = VTK.HEX_27
            elif elementType == Gmsh.PRI_18:
                vtkTypes[i] = VTK.PRI_18
            elif elementType == Gmsh.PNT:
                vtkTypes[i] = VTK.PNT
            elif elementType == Gmsh.QUA_8:
                vtkTypes[i] = VTK.QUA_8
            elif elementType == Gmsh.HEX_20:
                vtkTypes[i] = VTK.HEX_20
            elif elementType == Gmsh.PRI_15:
                vtkTypes[i] = VTK.PRI_15
            else:
                raise ValueError('Unknown Element type.')
        unstructuredGridToVTK(
		    fileName,
		    *self.vertices,
		    self.elements,
		    self.offsets,
		    vtkTypes
	    )


class GmshParser:

    class DataParser:
        
        def __init__(self, file, dataSize) -> None:
            self.file = file
            if dataSize == '4':
                self.dataType = np.float16
            elif dataSize == '8':
                self.dataType = np.float32
            elif dataSize == '16':
                self.dataType = np.float64
            else:
                raise ValueError('Unsupported data size.')
            self.mesh = Mesh()

        def readNodes(self):
            raise NotImplementedError('readNodes must be implemented.')

        def readElements(self):
            raise NotImplementedError('readElements must be implemented.')
        
    class DataParserV2(DataParser):
        
        def readNodes(self):
            self.numNodes = int(pop(self.file))
            Vx = np.zeros((self.numNodes, 1), dtype=self.dataType)
            Vy = np.zeros((self.numNodes, 1), dtype=self.dataType)
            Vz = np.zeros((self.numNodes, 1), dtype=self.dataType)
            
            line = pop(self.file)
            while line != '$EndNodes':
                node = line.split(' ') 
                nodeId = int(node[0])
                pos = [float(p) for p in node[1:]]
                Vx[nodeId-1] = pos[0]
                Vy[nodeId-1] = pos[1]
                Vz[nodeId-1] = pos[2]

                line = pop(self.file)
            self.mesh.vertices = (Vx, Vy, Vz)

        def readElements(self):
            numElements = int(pop(self.file))
            elemenTypes = np.zeros(numElements, dtype=np.int8)
            elements = []
            offsets = np.zeros(numElements, dtype=np.int32)

            # Parser Ignores the tags for now!
            line = pop(self.file)
            while line != '$EndElements':
                element = [int(e) for e in line.split(' ')]
                elementNumber, elementType, numOfTags = element[:3] 
                
                elemenTypes[elementNumber-1] = elementType
                elements += [i - 1 for i in element[3 + numOfTags:]]
                if elementNumber == 1:
                    offset = 0
                else:
                    offset = offsets[elementNumber-2]
                if elementType == Gmsh.LIN_2:
                    offset += 2
                elif elementType == Gmsh.TRI_3:
                    offset += 3
                elif elementType == Gmsh.QUA_4:
                    offset += 4
                elif elementType == Gmsh.TET_4:
                    offset += 4
                elif elementType == Gmsh.HEX_8:
                    offset += 8
                elif elementType == Gmsh.PYR_5:
                    offset += 5
                elif elementType == Gmsh.PRI_6:
                    offset += 6
                elif elementType == Gmsh.LIN_3:
                    offset += 3
                elif elementType == Gmsh.TRI_6:
                    offset += 6
                elif elementType == Gmsh.QUA_9:
                    offset += 9
                elif elementType == Gmsh.TET_10:
                    offset += 10
                elif elementType == Gmsh.HEX_27:
                    offset += 27
                elif elementType == Gmsh.PRI_18:
                    offset += 18
                elif elementType == Gmsh.PNT:
                    offset += 1
                elif elementType == Gmsh.QUA_8:
                    offset += 8
                elif elementType == Gmsh.HEX_20:
                    offset += 20
                elif elementType == Gmsh.PRI_15:
                    offset += 15
                else:
                    print(elementType)
                    raise ValueError('Unknown Element type.')
                offsets[elementNumber-1] = offset
                line = pop(self.file)
            self.mesh.elements = np.asanyarray(elements, dtype=np.int32)
            self.mesh.offsets = offsets
            self.mesh.elementTypes = elemenTypes
            self.mesh.version = '2.2'
        
    class DataParserV4(DataParser):
        
        def readNodes(self):
            raise NotImplementedError('readNodes must be implemented.')

        def readElements(self):
            raise NotImplementedError('readElements must be implemented.')

    def __init__(self) -> None:
        self.file = None

    def readMeshFormat(self):
        format = pop(self.file).split(' ')
        self.version, self.fileType, self.dataSize = format
        if self.fileType != '0':
            raise ValueError('Binary file format is not supported.')
        endFormat = pop(self.file)
        if endFormat != '$EndMeshFormat':
            raise SyntaxError('MeshFormat section does not terminate.')
        return self.version
    
    def parse(self, fileName):
        with open(fileName) as self.file:
            line = pop(self.file)
            while line:
                if line == '$MeshFormat':
                    version = self.readMeshFormat()
                    if version == '2.2':
                        self.dataParser = GmshParser.DataParserV2(self.file, self.dataSize)
                    elif version == '4.1':
                        self.dataParser = GmshParser.DataParserV4(self.file, self.dataSize)
                    else:
                        raise ValueError('Unsupported version.')
                if line == '$Nodes':
                    self.dataParser.readNodes()
                if line == '$Elements':
                    self.dataParser.readElements()
                line = pop(self.file)

def pop(file) -> str:
    return file.readline().strip()

def read(fileName):
    parser = GmshParser()
    parser.parse(fileName)
    return parser.dataParser.mesh