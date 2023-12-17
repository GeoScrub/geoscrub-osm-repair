"""
OSM Repair Tool

Author: John Lister - John.Lister@GeoScrub.org
Description: This script identifies and mitigates duplicate way warnings in OSM files.

MIT License

Copyright (c) 2023 GeoScrub L.L.C.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Standard Library Imports
from datetime import datetime
import logging
import argparse
import sys
import os

# Supporting Imports
from function_helper import *
from spatial_files import *

def main():
    print("Drag and drop your OSM file into the terminal, then press Enter.")
    input_osm_file = input().strip()

    data_directory = os.path.join("..", "data")
    # get working directory
    working_directory = os.getcwd()

    # Check if input_osm_file is .osm
    if not is_osm_file(input_osm_file):
        logging.error(f"{input_osm_file} is not a .osm file")
        sys.exit(1)
    
     # Setup Logging
    print("Setting up logging...")
    log_file = os.path.join(working_directory, f"logging/logging_{datetime.now().strftime('%Y%m%d%H%M%S')}.log")
    print(log_file)
    logging.basicConfig(filename=log_file,
                            level=logging.DEBUG,
                            format='%(asctime)s [%(levelname)s]: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
    
    # Setup Output Filenames
    print("Setting up output filenames...")
    duplicate_way_file = os.path.join(data_directory, input_osm_file.replace(".osm", "_duplicate_ways.shp"))
    repaired_osm_file = os.path.join(data_directory, input_osm_file.replace(".osm", "_repaired.osm"))
    
    # Derive and validate xml tree and root
    try:
        print("Deriving and validating xml tree and root...")
        tree, root = derive_tree_and_root(input_osm_file)
    except ET.ParseError as e:
        logging.error(f"Error parsing {input_osm_file}: {e}")
        raise ValueError(f"Error parsing {input_osm_file}: {e}")
    
    # Build Nodes
    try:
        print("Building nodes...")
        node_gdf = parse_osm_nodes(input_osm_file)
    except Exception as e:
        logging.error(f"Error processing nodes in {input_osm_file}: {e}")
        raise ValueError(f"Error processing nodes in {input_osm_file}: {e}")
    
    # Build Ways
    try:
        print("Building ways...")
        way_gdf, way_nodes = parse_osm_ways(input_osm_file, node_gdf)
    except Exception as e:
        logging.error(f"Error processing ways in {input_osm_file}: {e}")
        raise ValueError(f"Error processing ways in {input_osm_file}: {e}")
    
    # Identify Ways with duplicate geometries
    # 1. Identify duplicate geometries
    print("Identifying duplicate geometries...")
    duplicate_way_sets = find_duplicate_way_sets(way_nodes)
    number_of_duplicate_ways = len(duplicate_way_sets)
    print(f"Found {number_of_duplicate_ways} duplicate way sets:")
    if number_of_duplicate_ways < 1:
        print("No duplicate way sets found.")
        sys.exit(0)
    
    # 2. Export duplicate ways to shapefile
    try:
        print("Exporting duplicate ways to shapefile...")
        filter_and_save_duplicate_ways(way_gdf, duplicate_way_sets, duplicate_way_file)
    except Exception as e:
        logging.error(f"Error exporting duplicate ways to shapefile: {e}")
        raise ValueError(f"Error exporting duplicate ways to shapefile: {e}")
    
    # 3. Repair the OSM file
    try:
        print("Repairing OSM file...")
        relation_ways_to_remove =  process_relation_ways(root, duplicate_way_sets, way_gdf)
        remove_ways_and_save_xml(root, tree, relation_ways_to_remove, repaired_osm_file)
    except Exception as e:
        logging.error(f"Error repairing OSM file: {e}")
        raise ValueError(f"Error repairing OSM file: {e}")
    
    # Output Message
    print("{} has been repaired.\n{} has been created\n{} duplicate ways have been removed\nAny questions reach out to www.GeoScrub.org".format(input_osm_file, repaired_osm_file, number_of_duplicate_ways))


if __name__ == "__main__":
    main()

    
