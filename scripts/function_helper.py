import xml.etree.ElementTree as ET
import geopandas as gpd

# Function to test if test_osm_file file is .osm
def is_osm_file(test_osm_file_path: str) -> bool:
    return test_osm_file_path.endswith(".osm")

def derive_tree_and_root(test_osm_file_path: str) -> (ET.ElementTree, ET.Element):
    tree = ET.parse(test_osm_file_path)
    root = tree.getroot()
    return tree, root


def find_duplicate_way_sets(way_nodes) -> list:
    # Create a dictionary to store lists and their corresponding keys
    list_dict = {}

    for key, value in way_nodes.items():
        # Convert the list to a frozenset to make it hashable and order-insensitive
        value_set = frozenset(value)

        # Check if the set is already in the dictionary
        if value_set in list_dict:
            # Append the current key to the existing list
            list_dict[value_set].append(key)
        else:
            # Create a new list with the current key
            list_dict[value_set] = [key]

    # Filter out entries where the set has duplicates
    duplicate_sets = {key: keys for key, keys in list_dict.items() if len(keys) > 1}

    # Extract the keys with sets of identical values
    result_keys = [keys for keys in duplicate_sets.values()]

    return result_keys

def find_pair(lst_of_lists: list, target_value: str) -> str or None:
    for sublist in lst_of_lists:
        if target_value in sublist:
            # Return the other item in the list
            return next(item for item in sublist if item != target_value)
    # If the target_value is not found in any sublist None
    return None



def process_relation_ways(root: ET.Element, result_keys: list, way_gdf: gpd.GeoDataFrame) -> list:
    # Declare a list of way ids to remove
    relation_ways_to_remove = []

    # Process the specified "way" elements and associated "nd" elements in each "relation"
    for relation_element in root.findall(".//relation"):
        relation_id = relation_element.get("id")
        members = relation_element.findall(".//member")

        for member in members:
            # Check if a way member is in the result_keys
            if member.get("type") == "way":
                other_item = find_pair(result_keys, member.get("ref"))

                # If it"s a duplicate way
                if other_item:
                    member_way_id = member.get("ref")

                    if way_gdf.loc[way_gdf["id"] == other_item]["has_tag"].values[0]:
                        # Remove the way that equals member.get("ref")
                        relation_ways_to_remove.append(member_way_id)

                        # Change the member.get("ref") to equal the other item
                        member.set("ref", other_item)

    return relation_ways_to_remove


def remove_ways_and_save_xml(root: ET.Element, tree: ET.ElementTree, relation_ways_to_remove: list, output_file_path: str):
    # Remove the specified "way" elements and associated "nd" elements
    for way_element in root.findall(".//way"):
        way_id = way_element.get("id")
        if way_id in relation_ways_to_remove:
            root.remove(way_element)
            for nd_element in way_element.findall(".//nd"):
                way_element.remove(nd_element)

    # Save the modified XML to a new file
    tree.write(output_file_path)