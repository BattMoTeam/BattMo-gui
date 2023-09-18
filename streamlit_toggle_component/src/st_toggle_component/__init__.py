from pathlib import Path
from typing import List, Dict, Optional, Callable, Any, Tuple

import streamlit as st
import streamlit.components.v1 as components

# Tell streamlit that there is a component called st_toggle_component,
# and that the code to display that component is in the "frontend" folder
frontend_dir = (Path(__file__).parent / "frontend").absolute()
_component_func = components.declare_component(
	"st_toggle_component", path=str(frontend_dir)
)

# Create the python function that will be called
def st_toggle_component(
    labels: List[str],
    id : int,
    initial_values: List[bool],
    key: Optional[str] = None,
    quantity: Optional[int] = 3,
    limit: Optional[int] = 2,
    on_change: Optional[Callable[..., None]] = None,
    args: Optional[Tuple[Any, ...]] = None
)-> Dict[str, bool]:
    
    # if args is None:
    #     args = ()  # Initialize args as an empty tuple if not provided
    

    # Ensure the number of labels matches the number of values
    if len(labels) != len(initial_values):
        raise ValueError("Number of labels must match number of values")

    # Create a dictionary from labels and values
    toggle_dict = {label: value for label, value in zip(labels, initial_values)}

    if on_change is not None and args is not None:
        on_change(*args)  # Call the on_change function with arguments

    """
    Add a descriptive docstring
    """
    component_value = _component_func(
        labels = labels,
        id= id,
        initial_values = toggle_dict,
        key=key,
        quantity = quantity,
        limit=limit,
        on_change = None,
        args = args,
        default = toggle_dict
    )
    
    
    
    return component_value


def main():
    st.write("## Example")
    value = st_toggle_component(["Toggle1","Toggle2","Toggle3"], [False,False,False])
    
    st.write(value)



if __name__ == "__main__":
    main()


# print("value_=",value)
    # print("session =", st.session_state.states_ne)
    # if value != st.session_state.states_ne:
    #     st.session_state.states_ne = value
    #     st.experimental_rerun()