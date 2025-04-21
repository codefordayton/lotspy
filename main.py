""" flask_example.py

    Required packages:
    - flask
    - folium

    Usage:

    Start the flask server by running:

        $ python flask_example.py

    And then head to http://127.0.0.1:5000/ in your browser to see the map displayed

"""

from flask import Flask, render_template_string

import folium
from folium.plugins import FastMarkerCluster

import pandas as pd
app = Flask(__name__)


@app.route("/")
def fullscreen():
    """Simple example of a fullscreen map."""
    m = folium.Map(
        location=[39.7589, -84.1916],
        zoom_start=12,
    )
    # load the data/registry file into a pandas dataframe
    df = pd.read_json("data/registry.json")

    # add the data to the map
    callback = ('function (row) {' 
                'var marker = L.marker(new L.LatLng(row[0], row[1]), {color: "red"});'
                'var icon = L.AwesomeMarkers.icon({'
                "icon: 'info-sign',"
                "iconColor: row[3] === 'EXCEPTION' ? 'red' : 'white',"
                "markerColor: row[3] === 'EXCEPTION' ? 'red' : 'green',"
                "prefix: 'glyphicon',"
                "extraClasses: 'fa-rotate-0'"
                    '});'
                'marker.setIcon(icon);'
                "var popup = L.popup({maxWidth: '300'});"
                "const display_text = {text: row[2]};"
                "var mytext = $(`<div id='mytext' class='display_text' style='width: 100.0%; height: 100.0%;'> ${display_text.text}</div>`)[0];"
                "popup.setContent(mytext);"
                "marker.bindPopup(popup);"
                'return marker};')
    
    marker_cluster = FastMarkerCluster(data=df[['latitude', 'longitude', 'parcel', 'agent_type']].values.tolist(), callback=callback).add_to(m)

    # Add custom search control
    search_control = """
    <style>
    .search-container {
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 1000;
        background: white;
        padding: 10px;
        border-radius: 4px;
        box-shadow: 0 1px 5px rgba(0,0,0,0.65);
    }
    .search-input {
        padding: 6px;
        width: 200px;
    }
    </style>
    <div class="search-container">
        <input type="text" id="search-input" class="search-input" placeholder="Search for a parcel...">
    </div>
    <script>
    // Wait for the map and markers to be fully loaded
    window.addEventListener('load', function() {
        setTimeout(function() {
            // Find the map element (it's the first element with class 'folium-map')
            const map = document.querySelector('.folium-map');
            if (!map) return;  // Safety check
            
            // Get all markers directly
            const markers = document.getElementsByClassName('leaflet-marker-icon');
            
            document.getElementById('search-input').addEventListener('input', function(e) {
                const searchTerm = e.target.value.toLowerCase();
                console.log(searchTerm)
                Array.from(markers).forEach(marker => {
                    // Get the marker's associated popup content
                    const markerId = marker.src;
                    const popupContent = marker.parentElement.querySelector('.leaflet-popup-content');
                    
                    if (popupContent) {
                        const parcelText = popupContent.innerText.toLowerCase();
                        if (searchTerm === '' || parcelText.includes(searchTerm)) {
                            marker.style.display = '';  // Show marker
                            marker.style.visibility = 'visible';
                        } else {
                            marker.style.display = 'none';  // Hide marker
                            console.log('hide', parcelText)
                        }
                    }
                });
            });
        }, 1000); // Give time for markers to be created
    });
    </script>
    """
    
    m.get_root().html.add_child(folium.Element(search_control))

    return m.get_root().render()


@app.route("/iframe")
def iframe():
    """Embed a map as an iframe on a page."""
    m = folium.Map()

    # set the iframe width and height
    m.get_root().width = "800px"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()

    return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <head></head>
                <body>
                    <h1>Using an iframe</h1>
                    {{ iframe|safe }}
                </body>
            </html>
        """,
        iframe=iframe,
    )


@app.route("/components")
def components():
    """Extract map components and put those on a page."""
    m = folium.Map(
        width=800,
        height=600,
    )

    m.get_root().render()
    header = m.get_root().header.render()
    body_html = m.get_root().html.render()
    script = m.get_root().script.render()

    return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <head>
                    {{ header|safe }}
                </head>
                <body>
                    <h1>Using components</h1>
                    {{ body_html|safe }}
                    <script>
                        {{ script|safe }}
                    </script>
                </body>
            </html>
        """,
        header=header,
        body_html=body_html,
        script=script,
    )


if __name__ == "__main__":
    app.run(debug=True)