import os
import geopandas as gpd
import geoplot as gplt
import httpx
import pandas as pd

from . import console


def _to_geojson_file(gdf, name: str):
    gdf.to_file(f"data/{name}.geo.json", driver="GeoJSON")


def _read_geojson_file(name: str):
    return gpd.read_file(f"data/{name}.geo.json", driver="GeoJSON")


def _exists_geojson(name: str):
    return os.path.exists(f"data/{name}.geo.json")


def _exists_csv(name: str):
    return os.path.exists(f"data/{name}.csv")


def create_contiguous_us_west():
    contiguous_usa = gpd.read_file(gplt.datasets.get_path("contiguous_usa"))
    west_states = [
        "California",
        "Nevada",
        "Oregon",
        "Washington",
        "Idaho",
        "Montana",
        "Utah",
        "Arizona",
        "New Mexico",
    ]
    contiguous_us_west = contiguous_usa[contiguous_usa.state.isin(west_states)]
    _to_geojson_file(contiguous_us_west, "contiguous_us_west")


def get_contiguous_us_west():
    return _read_geojson_file("contiguous_us_west")


def create_datacenters():
    url = "https://www.datacenters.com/api/v1/locations?query=&withProducts=false&showHidden=false&radius=0&bounds=&circleBounds=&polygonPath=&forMap=true"  # noqa

    response = httpx.get(url, timeout=httpx.Timeout(5, read=20))
    data = response.json()

    datacenters_df = pd.DataFrame(data["locations"])

    datacenters = gpd.GeoDataFrame(
        datacenters_df,
        geometry=gpd.points_from_xy(datacenters_df.longitude, datacenters_df.latitude),
        crs="EPSG:4326",  # Standard lon/lat coordinate reference system (CRS)
    )

    _to_geojson_file(datacenters, "datacenters")


def get_datacenters():
    return _read_geojson_file("datacenters")


def create_datacenters_west():
    # Only keep states from the US "West" states as defined here (states of interest):
    # https://droughtmonitor.unl.edu/CurrentMap/StateDroughtMonitor.aspx?West
    datacenters = get_datacenters()
    contiguous_us_west = get_contiguous_us_west()
    datacenters_west = gpd.sjoin(datacenters, contiguous_us_west, how="inner")
    _to_geojson_file(datacenters_west, "datacenters_west")


def get_datacenters_west():
    return _read_geojson_file("datacenters_west")


def create_drought():
    # Source data URL found here: https://droughtmonitor.unl.edu/DmData/GISData.aspx
    # `drought` contains 5 rows, one per drought intensity ("DM"), each associated
    # with a multi-polygon that contains the set of areas at that drought level.
    drought_url = "https://droughtmonitor.unl.edu/data/shapefiles_m/USDM_20210622_M.zip"
    drought = gpd.read_file(drought_url)
    # TODO: select drought data within `us_west` only.
    _to_geojson_file(drought, "drought")


def get_drought():
    return _read_geojson_file("drought")


def create_datacenters_d4():
    datacenters = get_datacenters()
    drought = get_drought()

    datacenters_with_dm = gpd.sjoin(datacenters, drought, how="inner", op="intersects")
    datacenters_d4 = datacenters_with_dm[datacenters_with_dm["DM"] == 4]
    datacenters_d4_df = pd.DataFrame(
        datacenters_d4.drop(columns=["geometry", "index_right", "OBJECTID", "DM"])
    )
    datacenters_d4_df.to_csv("data/datacenters_d4.csv")


def _exec(func, *, fmt="geojson"):
    name = func.__name__
    prefix = "create_"
    name = name[len(prefix) :]

    print(f"Creating {name}...", end=" ", flush=True)

    exists = {"geojson": _exists_geojson, "csv": _exists_csv}[fmt]
    if exists(name):
        console.info("Already exists!")
        return

    func()
    console.success("Done")


if __name__ == "__main__":
    _exec(create_contiguous_us_west)
    _exec(create_datacenters)
    _exec(create_datacenters_west)
    _exec(create_drought)
    _exec(create_datacenters_d4, fmt="csv")
