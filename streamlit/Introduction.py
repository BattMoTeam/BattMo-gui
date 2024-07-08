import os
from PIL import Image
import streamlit as st
import sys
import streamlit.components.v1 as components


##############################
# Page Config

st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "images", "battmo_logo.png"
        )
    ),
    # layout="wide"
)

##############################
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v
##############################

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# set config is done before import to avoid streamlit error
from app_scripts.app_controller import (
    set_heading,
    set_page_navigation,
    set_external_links,
    set_acknowlegent_info,
)
from app_scripts import app_view


def run_app():

    # Set Introduction page heading wil title, BattMo logo, and BattMo info.
    set_heading()

    app_view.st_space(space_width=3)

    # Set page navigation
    col = set_page_navigation()

    # Set external links to websites and documentation
    set_external_links()

    with st.sidebar:
        app_view.st_space(space_width=3)

        # Set funding acknowledgement
        set_acknowlegent_info()

    try:
        battery_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Battery Status</title>
        </head>
        <body>
            <h1>Battery Status</h1>
            <p id="battery-level"></p>
            <p id="charging-status"></p>
            <p id="charging-time"></p>
            <p id="discharging-time"></p>

            <script>
                navigator.getBattery().then(function(battery) {
                    function updateAllBatteryInfo() {
                        updateChargeInfo();
                        updateLevelInfo();
                        updateChargingInfo();
                        updateDischargingInfo();
                    }
                    updateAllBatteryInfo();

                    battery.addEventListener('chargingchange', function() {
                        updateChargeInfo();
                    });
                    function updateChargeInfo() {
                        document.getElementById('charging-status').textContent = 'Battery charging? ' + (battery.charging ? 'Yes' : 'No');
                    }

                    battery.addEventListener('levelchange', function() {
                        updateLevelInfo();
                    });
                    function updateLevelInfo() {
                        document.getElementById('battery-level').textContent = 'Battery level: ' + battery.level * 100 + '%';
                    }

                    battery.addEventListener('chargingtimechange', function() {
                        updateChargingInfo();
                    });
                    function updateChargingInfo() {
                        document.getElementById('charging-time').textContent = 'Charging time: ' + battery.chargingTime/60 + ' seconds';
                    }

                    battery.addEventListener('dischargingtimechange', function() {
                        updateDischargingInfo();
                    });
                    function updateDischargingInfo() {
                        document.getElementById('discharging-time').textContent = 'Discharging time: ' + battery.dischargingTime/60/60 + ' hour';
                    }
                });
            </script>
        </body>
        </html>
        """

        # Embed the HTML into the Streamlit app
        components.html(battery_html, height=400)

    except:
        pass


if __name__ == "__main__":
    run_app()
