import os
import importlib
import dataclasses
import logging
import xml.etree.ElementTree as ET
from communicator.cyclonedds.idl.idl_dataclass_map import idl_dataclass_map
from communicator.topics_and_errors import DDS_TOPICS
import typing
import cyclonedds.idl.types as ct
import cyclonedds.idl._type_helper as _th

_LOGGER = logging.getLogger(__name__)

class DataClassManager:
    def __init__(self):
        self._data_class_cache = {}

    def get_data_class(self, class_name):
        """
        Dynamically imports and returns a data class based on its name.
        """
        if class_name in self._data_class_cache:
            return self._data_class_cache[class_name]

        module_name = idl_dataclass_map.get(class_name)
        if not module_name:
            raise ImportError(f"No module found for class {class_name}")

        module = importlib.import_module(module_name)
        data_class = getattr(module, class_name, None)
        if not data_class:
            raise ImportError(f"Class {class_name} not found in module {module_name}")

        self._data_class_cache[class_name] = data_class
        return data_class

    def create_zeroed_dataclass(self, cls: type) -> any:
        """Create an instance of a dataclass with all fields set to default 'zero' values based on their type."""
        field_defaults = {}
        for field in dataclasses.fields(cls):
            field_type = field.type

            # Get the base type and annotations if it's an annotated type
            if _th.get_origin(field_type) is _th.Annotated:
                base_type, *annotations = _th.get_args(field_type)
                custom_type = annotations[0] if annotations else base_type
            else:
                base_type, custom_type = field_type, field_type

            # Debugging
            _LOGGER.debug(f"Zero out Field: {field.name}, Base type: {base_type}, Custom type: {custom_type}, misc: {base_type}")

            #check if the field is array
            if base_type is int:
                default_value = 0
            elif base_type is float:
                default_value = 0.0
            elif isinstance(base_type, str):
                #Check if we have dataclass instance, Idn why the dataclass name goes as a string, a bit confusing 
                if base_type.rsplit('.', 1)[-1] in idl_dataclass_map:
                    dataclass_name = base_type.rsplit('.', 1)[-1]
                    dataclass_factory = self.get_data_class(dataclass_name)
                    default_value = self.create_zeroed_dataclass(dataclass_factory)
                else:
                    default_value = ""
            elif issubclass(_th.get_origin(base_type), typing.Sequence):
                
                custom_element_subtype = custom_type.subtype
                custom_element_length = custom_type.length
                element_type = _th.get_args(base_type)[0]

                if _th.get_origin(element_type) is _th.Annotated:
                    element_type = _th.get_args(element_type)[0]

                # _LOGGER.debug(f"ARRAY: element_type: {element_type}, length: {custom_element_length}")

                if element_type is int:
                    element_default = [0 for _ in range(custom_element_length)]
                    default_value = element_default
                elif element_type is float:
                    element_default = [0.0 for _ in range(custom_element_length)]
                    default_value = element_default
                elif isinstance(base_type, str):
                    element_default = ["" for _ in range(custom_element_length)]
                    default_value = element_default

                #this part will recursively zero out the included dataclasses
                elif isinstance(element_type, typing.ForwardRef):
                    dataclass_name = custom_element_subtype.rsplit('.', 1)[-1]
                    dataclass_factory = self.get_data_class(dataclass_name)
                    default_value = [self.create_zeroed_dataclass(dataclass_factory) for _ in range(custom_element_length)]
            else:
                default_value= None

            field_defaults[field.name] = default_value

        return cls(**field_defaults)
    

def get_topic_by_name(name):
    if name in DDS_TOPICS:
        return DDS_TOPICS[name]
    else:
        raise ValueError("DDS topic does not exist")



def cyclondds_xml_set(interface):

    current_path = os.path.dirname(os.path.abspath(__file__))
    cyclonedds_config_path = os.path.join(current_path, "cyclonedds.xml")
    tree = ET.parse(cyclonedds_config_path)
    root = tree.getroot()

    # Find the NetworkInterface element and change its name attribute
    for network_interface in root.findall(".//NetworkInterface"):
        network_interface.set("name", interface)  # Change the interface name

    # Save the modified XML back to the file
    tree.write(cyclonedds_config_path)

    # Set the CYCLONEDDS_URI environment variable to point to the updated config file
    os.environ['CYCLONEDDS_URI'] = cyclonedds_config_path
    _LOGGER.debug(f"CYCLONEDDS_URI set to: {cyclonedds_config_path}")

    _LOGGER.info(f"DDS Domain configured with network interface {interface}")