from enum import Enum
import json
import toml

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

class Type(Enum):
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
    ARRAY = 13

    def to_dict(self):
        if self == Type.FLOW:
            return "flow"

        elif self == Type.WILDCARD:
            return "wildcard"

        elif self == Type.ANY:
            return "any"

        elif self == Type.ANY_OR_FLOW:
            return "any_or_flow"

        else:
            return {"data": self.name.lower()}

    def __str__(self):
        # return self.name.lower()
        return self.to_dict()

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

    # @classmethod
    # def from_dict(cls, data):
    #     return cls.from_str(data["data"])

class IntrepidType:
    def __init__(self, base_type: Type, is_array=False):
        """
        Initialize a DataType.

        :param base_type: The base type, either a BaseDataType.
        :param container_type: Whether this is a container type like an array.
        """
        if not isinstance(base_type, Type):
            raise ValueError("base_type must be a BaseDataType")
        self.base_type = base_type
        self.container_type = is_array

    def is_array(self):
        """
        Check if this DataType is an array.
        """
        return self.container_type

    def is_flow(self):
        return self.base_type == Type.FLOW

    def to_dict(self):
        """
        Convert the IntrepidType to a dictionary representation.
        """
        base_dict = self.base_type.to_dict()
        result = {"type": base_dict}

        if not self.is_array():
            return result["type"]
        else:
            return result["type"]

    @classmethod
    def from_dict(cls, data):
        """
        Create a DataType from a dictionary representation.
        """
        if data.get("type") == "array":
            base_type = cls.from_dict(data.get("of"))
            return cls(base_type, container_type=True)
        else:
            base_type_name = data.get("type").upper()
            if base_type_name in Type.__members__:
                return cls(Type[base_type_name])
            raise ValueError(f"Invalid base type: {base_type_name}")

    def __str__(self):
        """
        String representation of IntrepidType.
        """
        if self.is_array():
            # return f"array<{self.base_type}>"
            return f"array<{self.base_type.name.lower()}>"
        return self.base_type.name.lower()
        # return str(self.base_type)  # Return the string representation of the base type

    def __eq__(self, other):
        """
        Equality comparison for IntrepidType.
        """
        return isinstance(other, IntrepidType) and self.base_type == other.base_type and self.container_type == other.container_type

    def to_python_type(self):
        if self.base_type == Type.INTEGER:
            return int
        if self.base_type == Type.FLOAT:
            return float
        if self.base_type in [Type.BIVEC2, Type.BIVEC3, Type.VEC2, Type.VEC3]:
            return list
        if self.base_type == Type.BOOLEAN:
            return bool
        return any

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

    def __init__(self, label: str, type: IntrepidType):
        self.label = label
        self.type = type

    def to_dict(self):
        result = {}
        result["label"] = self.label
        result["type"] = self.type.to_dict()
        if self.type.is_array():
            result["container"] = "array"
        return result

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

    def __init__(self, type: str = ""):
        self.inputs = []
        self.outputs = []
        self.type = type
        self.description = ""
        self.label = ""

    def add_label(self, label: str):
        self.label = label

    def add_description(self, description: str):
        self.description = description

    def add_input(self, label: str, type: Type):
        element = DataElement(label, type)
        self.inputs.append(element)
        # self.inputs.sort(key=lambda x: x.name)

    def add_output(self, label: str, type: Type):
        element = DataElement(label, type)
        self.outputs.append(element)
        # self.outputs.sort(key=lambda x: x.name)

    def get_inputs(self):
        """
            Retrieves the list of input elements for the node.

            Each input is represented as a tuple containing:
            - The index of the input (integer)
            - The label of the input (string)
            - The data type of the input (IntrepidType)

            Returns:
                list: A list of tuples representing the inputs. Each tuple contains:
                    - index (int): The index of the input element.
                    - label (str): The label (name) of the input element.
                    - type (IntrepidType): The data type of the input element.
        """
        return [(index, element.label, element.type) for index, element in enumerate(self.inputs)]

    def get_outputs(self):
        """
        Retrieves the list of output elements for the node.

        Each output is represented as a tuple containing:
        - The index of the output (integer)
        - The label of the output (string)
        - The data type of the output (IntrepidType)

        Returns:
            list: A list of tuples representing the outputs. Each tuple contains:
                - index (int): The index of the output element.
                - label (str): The label (name) of the output element.
                - type (IntrepidType): The data type of the output element.
        """

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

    def from_def(self, path: str):
        config = toml.load(path)
        # Set node type
        node_config = config.get("node", {})
        self.type = node_config.get("type", "")
        self.label = node_config.get("label", "")
        self.description = node_config.get("description", "")

        # Add inputs
        for input_name, input_spec in config.get("inputs", {}).items():
            if isinstance(input_spec, str):
                itype = input_spec  # TODO
                is_array = False
            else:
                itype = input_spec.get("type")
                is_array = input_spec.get("is_array")
            self.add_input(input_name, IntrepidType(Type.from_str(itype), is_array))

        # Add outputs
        for output_name, output_spec in config.get("outputs", {}).items():
            if isinstance(output_spec, str):
                itype = output_spec  # TODO
                is_array = False
            else:
                itype = output_spec.get("type")
                is_array = output_spec.get("is_array")
                # is_array = input_spec.get("is_array", True)
                # print(itype)
            # print(output_name, IntrepidType(Type.from_str(itype), is_array))
            self.add_output(output_name, IntrepidType(Type.from_str(itype), is_array))

    def __str__(self):
        """
        String representation of Intrepid Node.
        """
        node_type = self.type

        # Create input and output lists
        input_data = [(input_index, label, input_type) for input_index, label, input_type in self.get_inputs()]
        output_data = [(output_index, label, output_type) for output_index, label, output_type in self.get_outputs()]

        # Find the max length for each column
        idx_width = max(len(str(item[0])) for item in input_data + output_data)
        label_width = max(len(str(item[1])) for item in input_data + output_data)
        type_width = max(len(str(item[2])) for item in input_data + output_data)

        # Format headers
        header_str = f"{'IDX':<{idx_width}}\t{'LABEL':<{label_width}}\t{'TYPE':<{type_width}}"

        # Format inputs and outputs
        input_str = "\n".join([f"{input_index:<{idx_width}}\t{label:<{label_width}}\t{str(input_type):<{type_width}}"
                            for input_index, label, input_type in input_data])

        output_str = "\n".join([f"{output_index:<{idx_width}}\t{label:<{label_width}}\t{str(output_type):<{type_width}}"
                                for output_index, label, output_type in output_data])

        # Combine the node type, header, and input/output data
        return f"\nNode Type: {node_type}\n\nInputs:\n{header_str}\n{input_str}\n\nOutputs:\n{header_str}\n{output_str}"



if __name__ == '__main__':
    n0 = Node()
    n0.from_def("examples/node_definition.toml")
    print(n0)
