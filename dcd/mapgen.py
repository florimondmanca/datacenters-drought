import geoplot as gplt
import geoplot.crs as gcrs
import mapclassify as mc
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from . import datasrc

if __name__ == "__main__":
    # Draw USA West basemap.
    contiguous_us_west = datasrc.get_contiguous_us_west()
    extent = contiguous_us_west.total_bounds  # Used to fit other plots.
    ax = gplt.polyplot(
        contiguous_us_west,
        projection=gcrs.AlbersEqualArea(),
        linewidth=0.5,
        edgecolor="black",
        zorder=0,
    )

    # Overlay drought areas, colored by intensity.
    # See: https://residentmario.github.io/geoplot/plot_references/plot_reference.html#choropleth
    drought_us_west = datasrc.get_drought_us_west()
    # Custom cmap with alpha.
    cmap = plt.cm.get_cmap("YlOrRd")
    cmap_colors = cmap(np.arange(cmap.N))
    cmap_colors[:, 3] = 0.8  # Set a in (r, g, b, a)
    gplt.choropleth(
        drought_us_west,
        hue="DM",
        cmap=ListedColormap(cmap_colors),
        legend=True,
        scheme=mc.FisherJenks(drought_us_west["DM"], k=5),  # 5-category legend
        legend_kwargs={"bbox_to_anchor": (0.8, 0.7)},
        legend_labels=[
            "D0 (Abnormally Dry)",
            "D1 (Moderate Drought)",
            "D2 (Severe Drought)",
            "D3 (Extreme Drought)",
            "D4 (Exceptional Drought)",
        ],
        zorder=1,
        ax=ax,
        extent=extent,
    )
    # Draw drought area outlines
    gplt.polyplot(
        drought_us_west,
        linewidth=1,
        edgecolor="dimgray",
        zorder=1,
        ax=ax,
        extent=extent,
    )

    # Overlay datacenters in US West on map.
    datacenters_west = datasrc.get_datacenters_west()
    gplt.pointplot(
        datacenters_west,
        zorder=2,
        linewidth=0.8,
        s=5,  # marker size
        color="white",
        edgecolor="black",
        ax=ax,
        extent=extent,
    )

    plt.savefig("out/result.svg")
