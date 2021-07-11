import mapclassify as mc
import matplotlib.pyplot as plt
import geoplot as gplt
import geoplot.crs as gcrs

from . import datasrc

# 1) Load datacenter data.
datacenters_west = datasrc.get_datacenters_west()

# 2) Draw USA West basemap.
contiguous_us_west = datasrc.get_contiguous_us_west()
ax = gplt.polyplot(
    contiguous_us_west,
    projection=gcrs.AlbersEqualArea(),
    linewidth=0.5,
    zorder=1,
)

# 3) Overlay drought data.
drought_us_west = datasrc.get_drought_us_west()

# Draw drought areas colored by drought intensity.
# See: https://residentmario.github.io/geoplot/plot_references/plot_reference.html#choropleth
gplt.choropleth(
    drought_us_west,
    hue="DM",
    cmap="YlOrRd",  # Light yellow to dark red
    legend=True,
    scheme=mc.FisherJenks(drought_us_west["DM"], k=5),  # 5-category legend
    legend_kwargs={"bbox_to_anchor": (1, 0.35)},
    legend_labels=[
        "D0 (Abnormally Dry)",
        "D1 (Moderate Drought)",
        "D2 (Severe Drought)",
        "D3 (Extreme Drought)",
        "D4 (Exceptional Drought)",
    ],
    ax=ax,
    zorder=0,
)

# 4) Overlay datacenters in US West on map.
gplt.pointplot(
    datacenters_west,
    ax=ax,
    zorder=2,
)

plt.savefig("out/result.svg")
