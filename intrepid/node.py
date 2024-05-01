from enum import Enum
import json

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class PrimitiveDataType:
    def __init__(self, type: str):
        self.type = type

    # def __str__(self):
    #     return {"data": self.type }

    def to_dict(self):
        return { "data": self.type }


class DataType(Enum):
    INTEGER = 1
    FLOAT = 2
    STRING = 3
    FLOW = 4
    WILDCARD = 5
    ANY = 6
    ANY_OR_FLOW = 7
    # DICT = 8

    def __str__ (self):
        if self == DataType.INTEGER:
            # pdt = PrimitiveDataType("integer")
            # return pdt.to_dict()
            return "integer"
        elif self == DataType.FLOAT:
            return "float"
        elif self == DataType.STRING:
            return "string"
        elif self == DataType.FLOW:
            return "flow"
        elif self == DataType.WILDCARD:
            return "wildcard"
        elif self == DataType.ANY:
            return "any"
        elif self == DataType.ANY_OR_FLOW:
            return "any_or_flow"
        # elif self == DataType.DICT:
        #     return "dict"
        else:
            return super().__str__()

    def to_dict(self):
        if self == DataType.INTEGER:
            return {"data": "integer"}
        elif self == DataType.FLOAT:
            return {"data": "float"}
        elif self == DataType.STRING:
            return {"data": "string"}
        elif self == DataType.FLOW:
            return {"data": "flow"}
        elif self == DataType.WILDCARD:
            return {"data": "wildcard"}
        elif self == DataType.ANY:
            return {"data": "any"}
        elif self == DataType.ANY_OR_FLOW:
            return {"data": "any_or_flow"}

class DataElement:
    """
     type PinSpec = {
        label:        string;
        description?: string;
        type:         { data: string } | 'flow' | 'wildcard' | 'any' | 'any_or_flow';
        container?:   'single' | 'option' | 'array' | 'any';
        count?:       'one' | 'zero_or_more';
        is_const?:    boolean;
    }
    """

    def __init__(self, label: str, type: DataType):
        self.label = label
        self.type = type

    def to_dict(self):
        if self.type == DataType.INTEGER:
            return {
                "label": self.label,
                "type": {
                    "data": "integer"
                    }
                }

        if self.type == DataType.FLOAT:
                    return {
                        "label": self.label,
                        "type": {
                            "data": "float"
                            }
                        }

        if self.type == DataType.STRING:
                    return {
                        "label": self.label,
                        "type": {
                            "data": "string"
                            }
                        }

        return {"label": self.label,
                "type": self.type}



class Node:
    """
    Intrepid Node spec
    -------------------------------

    type NodeSpec = {
        type:         string;
        label:        string;
        description?: string;
        inputs?:      PinSpec[];
        outputs?:     PinSpec[];
    }


    """

    def __init__(self, type: str):
        self.inputs = []
        self.outputs = []
        self.type = type
        self.description = ""
        self.label = ""


    def add_label(self, label: str):
        self.label = label

    def add_description(self, description: str):
        self.description = description

    def add_input(self, label: str, type: DataType):
        element = DataElement(label, type)
        self.inputs.append(element)
        # self.inputs.sort(key=lambda x: x.name)

    def add_output(self, label: str, type: DataType):
        element = DataElement(label, type)
        self.outputs.append(element)
        # self.outputs.sort(key=lambda x: x.name)

    def get_inputs(self):
        return [(index, element.label, element.type) for index, element in enumerate(self.inputs)]

    def get_outputs(self):
        return [(index, element.label, element.type) for index, element in enumerate(self.outputs)]

    def to_json(self):
        inputs_json = [input_element.to_dict() for input_element in self.inputs]
        outputs_json = [output_element.to_dict() for output_element in self.outputs]
        res = {
            "inputs": inputs_json,
            "outputs": outputs_json,
            "type": self.type,
            "label": self.label,
            "description": self.description
            }

        return json.dumps(res, cls=CustomEncoder)



if __name__ == '__main__':
    n0 = Node()
    n0.add_input("in1", DataType.INTEGER)
    n0.add_input("in2", DataType.FLOAT)
    # n0.add_input("in3", DataType.INTEGER)
    n0.add_output("out1", DataType.FLOAT)
    n0.get_inputs()
