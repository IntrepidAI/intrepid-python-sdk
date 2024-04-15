from enum import Enum



class DataType(Enum):
    INTEGER = 1
    FLOAT = 2
    STRING = 3
    # TODO

class DataElement:
    def __init__(self, name, data_type):
        self.name = name
        self.data_type = data_type


class Node:
    """
    Intrepid Node spec
    """

    def __init__(self):
        self.inputs = []
        self.outputs = []

    def add_input(self, name, data_type):
        element = DataElement(name, data_type)
        self.inputs.append(element)
        self.inputs.sort(key=lambda x: x.name)

    def add_output(self, name, data_type):
        element = DataElement(name, data_type)
        self.outputs.append(element)
        self.outputs.sort(key=lambda x: x.name)

    def get_inputs(self):
        return [(index, element.name, element.data_type) for index, element in enumerate(self.inputs)]

    def get_outputs(self):
        return [(index, element.name, element.data_type) for index, element in enumerate(self.outputs)]


if __name__ == '__main__':
    n0 = Node()
    n0.add_input("in1", DataType.INTEGER)
    n0.add_input("in2", DataType.INTEGER)
    n0.add_input("in3", DataType.INTEGER)
    n0.add_output("out1", DataType.FLOAT)
    n0.get_inputs()
