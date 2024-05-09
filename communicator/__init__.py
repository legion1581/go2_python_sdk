# communicator/__init__.py
import os
import sys

# Get the root of the project based on this file's directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
idl_path = os.path.join(project_root, 'communicator', 'cyclonedds', 'idl')
if idl_path not in sys.path:
    sys.path.insert(0, idl_path)
