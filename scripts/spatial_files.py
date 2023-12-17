from shapely.geometry import LineString, Point
import xml.etree.ElementTree as ET
import geopandas as gpd
import pandas as pd

def parse_osm_nodes(test_osm_file_path: str) -> gpd.GeoDataFrame:
    # List to store node attributes
    node_data = []

    # Parse the XML file
    for event, elem in ET.iterparse(test_osm_file_path):
        if elem.tag == "node":
            # Extract node attributes
            node_attrib = elem.attrib

            # Create a Point geometry for the node
            lon = float(node_attrib["lon"])
            lat = float(node_attrib["lat"])
            geometry = Point(lon, lat)

            # Add the node information to the list
            node_data.append({"id": node_attrib["id"], "lat": lat, "lon": lon, "geometry": geometry})

    # Create a GeoDataFrame from the list
    node_gdf = gpd.GeoDataFrame(node_data, geometry="geometry")

    # Set the coordinate reference system (CRS) for the GeoDataFrame
    # This assumes the data is in WGS84 (EPSG:4326)
    node_gdf.crs = "EPSG:4326"

    return node_gdf

def parse_osm_ways(test_osm_file_path: str, node_gdf: gpd.GeoDataFrame):
    WAY_GDF_FIELDS = ["id", "node_ids", "has_tag", "tags" ,"geometry"]
    # make empty geodataframe to store way geometries
    way_gdf = gpd.GeoDataFrame(columns=WAY_GDF_FIELDS)

    way_data = []
    way_nodes = {}

    for event, elem in ET.iterparse(test_osm_file_path):
        if elem.tag == "way":
            HAS_TAG = False

            way_id = elem.get("id")

            # check if way has a tag
            elem_tags = []
            if elem.find(".//tag") is not None:
                # Append the tag values to elem_tags
                elem_tags = [tag.get("k") for tag in elem.findall(".//tag") if tag.get("k") is not None]
                # Make a string of the tag values
                elem_tags_string = ", ".join(elem_tags)
                HAS_TAG = True
            
            # Extract and print each nd ref for the current way
            nd_refs = [nd.get("ref") for nd in elem.findall(".//nd")]

            # For each node in the way get the lat and lon from node_gdf
            # Using the lat lon make a polyline geometry and make a record in the way_gdf using the way_id and geometry
            way_node_ids = []
            way_geometry = []
            for nd_ref in nd_refs:
                node = node_gdf[node_gdf["id"] == nd_ref]
                lat = node["lat"].values[0]
                lon = node["lon"].values[0]
                way_node_ids.append(nd_ref)
                way_geometry.append((lon, lat))

            # Create a LineString geometry for the way
            way_geometry = LineString(way_geometry)

            # Add the way information to the list
            way_data.append({"id": way_id, "has_tag": HAS_TAG, "tags": elem_tags_string, "geometry": way_geometry})

            # Add the node ids to the way_nodes list
            way_nodes[way_id] = way_node_ids

    # Create a GeoDataFrame from the list
    way_gdf = gpd.GeoDataFrame(way_data, geometry="geometry", crs="EPSG:4326")

    return way_gdf, way_nodes

def filter_and_save_duplicate_ways(way_gdf: gpd.GeoDataFrame, result_keys: list, output_shapefile_path: str):
    # Filter the way_gdf DataFrame to only include the ids in the result_keys
    duplicate_ways = []
    for key_pair in result_keys:
        duplicate_ways.append(way_gdf[way_gdf["id"].isin(key_pair)])

    # Concatenate the duplicate_ways into a single DataFrame and preserve geometry
    duplicate_ways_df = pd.concat(duplicate_ways, ignore_index=True)

    # Create a new GeoDataFrame from the concatenated DataFrame
    duplicate_ways_gdf = gpd.GeoDataFrame(duplicate_ways_df, geometry="geometry")

    # Output the GeoDataFrame to a SHP file
    duplicate_ways_gdf.to_file(output_shapefile_path, driver="ESRI Shapefile")
