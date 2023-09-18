// The `Streamlit` object exists because our html file includes
// `streamlit-component-lib.js`.
// If you get an error about "Streamlit" not being defined, that
// means you're missing that file.

function onRender(event) {
  if (!window.rendered) {
    // Get the quantity and limit values from the event detail
    const { labels,id, initial_values, quantity, limit, on_change, args } = event.detail.args;  


    // Initialize an object to hold checkbox values
    const checkboxValues = {};
    // initial_values.forEach((value, index) => {
    //   checkboxValues[labels[index]] = value;
    // });

    // Function to send the values of all toggles to Streamlit
    const sendValues = () => {
      parent.postMessage({ sentinel: 'streamlit', ...checkboxValues[id] }, '*');
    };

    // Function to handle checkbox change events
    const handleCheckboxChange = (checkbox) => {
      const toggleId = checkbox.id;
      checkboxValues[toggleId] = checkbox.checked;

      // Count the number of selected checkboxes
      const selectedCount = Object.values(checkboxValues).filter((value) => value).length;

      // Enforce the limit on enabled checkboxes
      if (selectedCount > limit) {
        for (const key in checkboxValues) {
          if (checkboxValues.hasOwnProperty(key) && checkboxValues[key]) {
            checkboxValues[key] = false;
            document.getElementById(key).checked = false;
            break; // Stop after unchecking one checkbox
          }
        }
      }

      // Send the updated values to Streamlit
      sendValues();
      Streamlit.setComponentValue(checkboxValues);

      // Call the JavaScript function specified by on_change_str
      if (on_change) {
        on_change(args); // Call the function by its name
      }
      
      // const inputId = `input_${category_id}_${non_material_parameter.id}`;
      // const inputElement = document.getElementById(inputId);

      // // Update the disabled state of the input element based on the checkbox state
      // inputElement.disabled = !checkbox.checked;
    };

    // Get the container for toggles
    const toggleContainer = document.getElementById('toggle-container');

    // Create checkboxes based on the quantity argument
    for (let i = 0; i < quantity; i++) {
      const toggleId = labels[i]; // Use i to access the correct label from the labels array
      
      checkboxValues[toggleId] = false;

      // Create a label element for the checkbox
      const label = document.createElement('label');
      
      // Create a spacer element
      const spacer = document.createElement('div');
      spacer.style.width = '20px';

      // Create a checkbox element
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.id = toggleId;
      
      // Set the label text
      label.innerHTML = labels[i];  // Use i to access the correct label from the labels array

      // Associate the label with the checkbox using the "for" attribute
      label.setAttribute('for', checkbox.id);

      // Append the checkbox to the toggle container
      toggleContainer.appendChild(checkbox);
      toggleContainer.appendChild(label);
      toggleContainer.appendChild(spacer);
    }

    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach((checkbox) => {
      checkbox.addEventListener('change', () => {
        handleCheckboxChange(checkbox);
      });
    });

    // Initial data send
    sendValues();

    // You'll most likely want to pass some data back to Python like this
    // sendValue({output1: "foo", output2: "bar"})
    window.rendered = true;
  }
}

// Render the component whenever python send a "render event"
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
// Tell Streamlit that the component is ready to receive events
Streamlit.setComponentReady()
// Render with the correct height, if this is a fixed-height component
Streamlit.setFrameHeight(100)


 // const value = toggleValues
    
    // const input1 = document.getElementById("toggle1");
    //       if (value) {
    //         input1.value = value
    //       }

    // const input2 = document.getElementById("toggle2");
    // if (value) {
    //   input2.value = value
    // }

    // const input3 = document.getElementById("toggle3");
    //       if (value) {
    //         input3.value = value
    //       }
    
    // input1.onclick = event => sendValue(event.target.value)
    // input2.onclick = event => sendValue(event.target.value)
    // input2.onclick = event => sendValue(event.target.value)