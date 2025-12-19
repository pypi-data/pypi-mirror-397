import geopandas as gpd
from geopandas import GeoDataFrame
from pathlib import Path
from shapely.geometry import box


def normalize(file: Path, patch_size: int) -> GeoDataFrame:
    # Take some geojson and normalize it
    # so that it fits in a specific patch size.
    # This routine may need more work to be useful
    # for reintal layer workflow.

    # Read the (geo) json and modify it as needed.
    frame: GeoDataFrame = gpd.read_file(file)
    frame["geometry"] = frame.geometry.apply(square_centered, side=patch_size)

    return frame


def square_centered(geom, side):
    # Truncate the geometry to a square centered on the original
    # with a size of 'side' e.g. 512
    minx, miny, maxx, maxy = geom.bounds
    cx = (minx + maxx) / 2.0
    cy = (miny + maxy) / 2.0
    return box(cx - side / 2.0, cy - side / 2.0, cx + side / 2.0, cy + side / 2.0)
