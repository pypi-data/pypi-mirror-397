import os

import streamlit.components.v1 as components


# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "custom_context_menu",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
   _component_func = components.declare_component("custom_context_menu", path=build_dir)

def custom_context_menu(label="Right click", key=None):
    return _component_func(label=label, key=key)

