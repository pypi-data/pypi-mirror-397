"""
Chakra UI QML - A modern QML component library inspired by Chakra UI

This package provides a comprehensive set of QML components with a focus on
accessibility, themability, and developer experience.
"""

__version__ = "0.5.1"
__author__ = "ASLant"

from .CFrameless import CFrameless

# Available QML components (use in QML with: import Chakra 1.0)
COMPONENTS = [
    "CAlert", "CBadge", "CBox", "CButton", "CCard", "CCenter",
    "CCheckbox", "CContainer", "CFlex", "CIcon", "CInput",
    "CMenu", "CModal", "CProgress", "CScrollArea", "CSelect",
    "CSpinner", "CSwitch", "CTag", "CToast", "CWindow"
]

__all__ = ["CFrameless", "init", "COMPONENTS"]


def get_component_path():
    """Get the absolute path to the QML components directory."""
    import os
    return os.path.dirname(os.path.abspath(__file__))


def register_qml_types(module_name="Chakra", major_version=1, minor_version=0):
    """
    Register all QML types to the QML engine.
    
    Args:
        module_name: The QML module name (default: "Chakra")
        major_version: Major version number (default: 1)
        minor_version: Minor version number (default: 0)
    
    Example:
        >>> from PySide6.QtQml import qmlRegisterType
        >>> from chakra_ui_qml import register_qml_types
        >>> register_qml_types()
    """
    from PySide6.QtQml import qmlRegisterType
    qmlRegisterType(CFrameless, module_name, major_version, minor_version, "CFrameless")


def setup_qml_import_path(engine):
    """
    Add the component path to QML engine's import path.
    
    Args:
        engine: QQmlApplicationEngine instance
    
    Example:
        >>> from PySide6.QtQml import QQmlApplicationEngine
        >>> from chakra_ui_qml import setup_qml_import_path
        >>> engine = QQmlApplicationEngine()
        >>> setup_qml_import_path(engine)
    """
    import os
    component_path = get_component_path()
    parent_path = os.path.dirname(component_path)
    engine.addImportPath(parent_path)


def init(engine, module_name="Chakra", major_version=1, minor_version=0):
    """
    Initialize Chakra UI QML - register types and setup import path.
    
    This is a convenience function that combines register_qml_types() and
    setup_qml_import_path() into a single call.
    
    Args:
        engine: QQmlApplicationEngine instance
        module_name: The QML module name (default: "Chakra")
        major_version: Major version number (default: 1)
        minor_version: Minor version number (default: 0)
    
    Example:
        >>> from PySide6.QtQml import QQmlApplicationEngine
        >>> from chakra_ui import init
        >>> engine = QQmlApplicationEngine()
        >>> init(engine)
    """
    register_qml_types(module_name, major_version, minor_version)
    setup_qml_import_path(engine)
