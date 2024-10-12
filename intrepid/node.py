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
    BOOLEAN = 8
    VEC2 = 9
    VEC3 = 10
    BIVEC2 = 11
    BIVEC3 = 12

    def to_dict(self):
        if self == DataType.FLOW:
            return "flow"
        elif self == DataType.WILDCARD:
            return "wildcard"
        elif self == DataType.ANY:
            return "any"
        elif self == DataType.ANY_OR_FLOW:
            return "any_or_flow"
        else:
            return {"data": self.name.lower()}


    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_dict(cls, data):
        for enum_member in cls:
            if enum_member.name.lower() == data.get("data"):
                return enum_member
        raise ValueError("Invalid data type")

    @classmethod
    def from_str(cls, data):
        try:
            return cls[data.upper()]
        except KeyError:
            raise ValueError("Invalid data type")

    # def to_dict(self):
    #     return {"data": str(self)}

    # @classmethod
    # def from_dict(cls, data):
    #     return cls.from_str(data["data"])

class DataElement:
    """
     type PinSpec = {
        label:        string;
        description?: string;
        type:         { data: string} | 'flow' | 'wildcard' | 'any' | 'any_or_flow';
        container?:   'single' | 'option' | 'array' | 'any';
        count?:       'one' | 'zero_or_more';
        is_const?:    boolean;
    }
    """

    def __init__(self, label: str, type: DataType):
        self.label = label
        self.type = type

    def to_dict(self):
        # if self.type == DataType.INTEGER:
        #     return {
        #         "label": self.label,
        #         "type": {
        #             "data": "integer"
        #             }
        #         }

        # if self.type == DataType.FLOAT:
        #             return {
        #                 "label": self.label,
        #                 "type": {
        #                     "data": "float"
        #                     }
        #                 }
        # if self.type == DataType.BOOLEAN:
        #                     return {
        #                         "label": self.label,
        #                         "type": {
        #                             "data": "boolean"
        #                             }
        #                         }
        # if self.type == DataType.STRING:
        #             return {
        #                 "label": self.label,
        #                 "type": {
        #                     "data": "string"
        #                     }
        #                 }

        return {"label": self.label,
                "type": self.type.to_dict()}



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

    def get_type(self) -> str:
        return self.type

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

    def to_dict(self) -> dict:
        inputs_json = [input_element.to_dict() for input_element in self.inputs]
        outputs_json = [output_element.to_dict() for output_element in self.outputs]
        res = {
            "inputs": inputs_json,
            "outputs": outputs_json,
            "type": self.type,
            "label": self.label,
            "description": self.description
            }
        return res

if __name__ == '__main__':
    n0 = Node()
    n0.add_input("in1", DataType.INTEGER)
    n0.add_input("in2", DataType.FLOAT)
    # n0.add_input("in3", DataType.INTEGER)
    n0.add_output("out1", DataType.FLOAT)
    n0.get_inputs()
