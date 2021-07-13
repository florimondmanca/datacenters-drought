import folium
from folium.plugins import MarkerCluster

from . import datasrc

if __name__ == "__main__":
    # Create map
    m = folium.Map(
        location=[41, -116],
        tiles="cartodbpositron",
        zoom_start=5,
        control_scale=True,
    )

    # Overlay drought areas, colored by intensity.
    # See: https://residentmario.github.io/geoplot/plot_references/plot_reference.html#choropleth
    drought_us_west = datasrc.get_drought_us_west()
    drought_data = drought_us_west.copy()
    drought_data["geoid"] = drought_data.index.astype(str)
    drought_data = drought_data[["geoid", "DM", "geometry"]]
    folium.Choropleth(
        geo_data=drought_data,
        data=drought_data,
        bins=6,
        columns=["geoid", "DM"],
        key_on="feature.id",
        fill_color="YlOrRd",
        line_color="darkgray",
        line_weight=2,
        legend_name="Drought level",
    ).add_to(m)

    # Show datacenters with name on map
    datacenters_west = datasrc.get_datacenters_west()
    dc_markers = MarkerCluster(
        name="Datacenters",
        # Option, see:
        # https://github.com/Leaflet/Leaflet.markercluster#options
        max_cluster_radius=25,
        disable_clustering_at_zoom=7,
    )
    for _, r in datacenters_west.iterrows():
        lat, lon = r["geometry"].coords[0]
        folium.Marker(
            location=(lon, lat),
            popup=r["name"],
        ).add_to(dc_markers)
    dc_markers.add_to(m)

    # Show controls for map layers.
    folium.LayerControl().add_to(m)

    m.save("out/index.html")
