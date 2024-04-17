# communicator/__init__.py
import os
import sys
import logging

logger = logging.getLogger(__name__)

def setup_import_paths():
    # Get the root of the project based on this file's directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    idl_path = os.path.join(project_root, 'communicator', 'idl')
    if idl_path not in sys.path:
        sys.path.insert(0, idl_path)
        # logger.info(f"Added {idl_path} to sys.path")
        print(f"Added {idl_path} to sys.path")

setup_import_paths()
