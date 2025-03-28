import os
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import geopandas as gpd
import pandas as pd
import scrapy
import scrapy.middleware
from scrapy.utils.project import data_path

from lotspy.items import ParcelItem


class ParcelsSpider(scrapy.Spider):
    name = "parcels"

    def start_requests(self):
        urls = [
            "https://go.mcohio.org/embed/auditor/downloads/Shape_files/SHAPEFILE_PARCELLINES_ROW_OLDLOT.zip",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        unzipped_path = data_path("shape_files", createdir=True)

        # if the unzipped dir is empty, unzip the files
        if not os.listdir(unzipped_path):
            with ZipFile(BytesIO(response.body), "r") as zip_ref:
                zip_ref.extractall(unzipped_path)

        # Read the shapefile
        gdf = gpd.read_file(Path(unzipped_path, "Parcels.shp"))

        # Get the original CRS
        original_crs = gdf.crs

        # Clean invalid geometries and calculate centroids
        original_count = len(gdf)
        gdf["centroid"] = gdf.geometry.apply(
            lambda geom: geom.centroid if geom and geom.is_valid else None
        )

        # Remove rows where centroid calculation failed
        gdf = gdf.dropna(subset=["centroid"])
        self.logger.warning(f"Dropped {original_count - len(gdf)} invalid geometries")

        # Create a new GeoDataFrame with just the centroids
        centroid_gdf = gpd.GeoDataFrame(
            gdf.drop(columns=["geometry"]), geometry="centroid", crs=original_crs
        )

        # Reproject to WGS84 (EPSG:4326)
        centroid_gdf = centroid_gdf.to_crs("EPSG:4326")

        # Extract latitude and longitude from centroids
        centroid_gdf["longitude"] = centroid_gdf.geometry.x
        centroid_gdf["latitude"] = centroid_gdf.geometry.y

        for _, row in centroid_gdf.iterrows():
            yield ParcelItem(
                parcel=row["TAXPINNO"],
                longitude=row["longitude"],
                latitude=row["latitude"],
                address=create_full_address(row),
            )


def create_full_address(row):
    """Combine address components into a single string."""
    components = []

    # Add number if present
    if pd.notna(row.get("LOC_NBR")):
        components.append(str(int(row["LOC_NBR"])))  # Convert to int to remove decimals

    # Add direction if present
    if pd.notna(row.get("LOC_DIR")):
        components.append(str(row["LOC_DIR"]))

    # Add street name if present
    if pd.notna(row.get("LOC_STREET")):
        components.append(str(row["LOC_STREET"]))

    # Add suffix if present
    if pd.notna(row.get("LOC_SUFFIX")):
        components.append(str(row["LOC_SUFFIX"]))

    return " ".join(components)
