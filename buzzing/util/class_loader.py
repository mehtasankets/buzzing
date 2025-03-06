import importlib
import logging
from typing import Type, Any

LOG = logging.getLogger(__name__)

def class_from_string(module_name: str, class_name: str) -> Type[Any]:
    """Dynamically load a class from a module.

    Args:
        module_name: Fully qualified module name (e.g. 'buzzing.bots.test_bot')
        class_name: Name of the class to load from the module

    Returns:
        The requested class type

    Raises:
        ImportError: If the module cannot be imported
        AttributeError: If the class does not exist in the module
        Exception: For any other unexpected errors
    """
    try:
        module = importlib.import_module(module_name)
        class_type = getattr(module, class_name)
        LOG.debug(f"Successfully loaded class {class_name} from module {module_name}")
        return class_type
    except ImportError as e:
        LOG.error(f"Failed to import module {module_name}: {e}")
        raise
    except AttributeError as e:
        LOG.error(f"Class {class_name} not found in module {module_name}: {e}")
        raise
    except Exception as e:
        LOG.error(f"Unexpected error loading class {class_name} from {module_name}: {e}")
        raise
