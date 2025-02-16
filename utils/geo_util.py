import os
from io import BytesIO

import matplotlib.pyplot as plt
from PIL import Image
from geopandas import GeoDataFrame


class GeoUtil:
    def __init__(self):
        pass

    @staticmethod
    def find_all_connected_road_groups(gdf: GeoDataFrame, start_index: int, max_length: float, min_length: float = 0.0,
                                       max_groups: int = 1000, types_filter: set = None):
        """
        Starting from a given road, find all connected road groups until the total length reaches `max_length` and satisfies the `min_length` requirement.

        Parameters:
            gdf (GeoDataFrame): GeoDataFrame containing road data.
            start_index (int): Index of the starting road.
            max_length (float): Maximum total length in meters.
            min_length (float): Minimum total length in meters.
            max_groups (int): Maximum number of road groups to include. Groups beyond this limit are discarded.
            types_filter (set): Set of road types to filter. Only roads of these types are included in the path.

        Returns:
            List[Set[int]]: A list of all possible road groups, where each group is a set of indices.
        """
        if types_filter is not None:
            filtered_gdf = gdf[gdf['type'].isin(types_filter)]
        else:
            filtered_gdf = gdf

        # 使用集合来存储已遍历的路径，避免重复
        visited_paths = set()

        def backtrack(current_index, current_road_group, current_length, all_road_groups, level=0):
            '''
            Recursive function to search for all possible paths.
            :param current_index: Starting index of the road group.
            :param current_road_group: Current road group.
            :param current_length: Total length of the current road group.
            :param all_road_groups: List to store all paths.
            :return:
            '''

            # If the number of groups exceeds the maximum limit, stop searching to avoid excessive data (may miss some paths) TODO
            all_road_groups_count = len(all_road_groups)
            if all_road_groups_count >= max_groups:
                return

            # If the current length exceeds max_length, stop further searching
            if current_length >= max_length:
                return

            # If the current length satisfies min_length, add the current path to the results
            if current_length >= min_length:
                current_road_group_set = frozenset(current_road_group)
                if current_road_group_set not in visited_paths:  # Check if it already exists
                    visited_paths.add(current_road_group_set)
                    all_road_groups.append(current_road_group_set)

            # Get the geometry of the current road
            current_geometry = gdf.iloc[current_index].geometry
            # Find all roads in the filtered GeoDataFrame that touch the current road
            touching_roads = filtered_gdf[filtered_gdf.touches(current_geometry)]

            for _, road in touching_roads.iterrows():
                road_index = road.name  # Get the index of the road
                if road_index not in current_road_group:
                    # Update the path and length
                    current_road_group.append(road_index)
                    current_length += road.geometry.length

                    # Recursively process the next road
                    backtrack(road_index, current_road_group, current_length, all_road_groups, level + 1)

                    # Backtrack
                    current_road_group.pop()
                    current_length -= road.geometry.length

        all_road_groups = []
        backtrack(start_index, [start_index], gdf.iloc[start_index].geometry.length, all_road_groups)
        return all_road_groups

    @staticmethod
    def convert_path_to_image(gdf: GeoDataFrame, path: set, draw_background=False, image_size: tuple = (10, 10),
                              path_color: str = 'black', path_width: float = 4) -> 'PIL.Image.Image':
        """
        Generate a path plot based on the given set of road indices and return a PIL.Image.Image object.

        Parameters:
            gdf (GeoDataFrame): GeoDataFrame containing road data.
            path (set): Set of road indices.
            draw_background (bool): Whether to draw the background.

        Returns:
            PIL.Image.Image: PIL.Image.Image object of the path plot.
        """
        fig, ax = plt.subplots(figsize=image_size)

        if draw_background:
            gdf.plot(ax=ax, color='black', linewidth=2)

        # Extract road data corresponding to the path from the GeoDataFrame and plot the path
        path_roads = gdf.iloc[list(path)]
        path_roads.plot(ax=ax, color=path_color, linewidth=path_width)

        ax.set_axis_off()

        # Save the image to memory
        img_buf = BytesIO()
        plt.savefig(img_buf, format='PNG', dpi=25, bbox_inches=None, pad_inches=0)
        plt.close()

        # Read the image from memory and convert it to a PIL.Image object
        img_buf.seek(0)
        return Image.open(img_buf).convert("RGB")

    @staticmethod
    def save_path_to_image(gdf: GeoDataFrame, path: set, output_image_file: str, draw_background=False,
                           image_size: tuple = (10, 10), path_color: str = 'black', path_width: float = 4):
        """
        Generate a path plot based on the given set of road indices and save it as an image.

        Parameters:
            gdf (GeoDataFrame): GeoDataFrame containing road data.
            path (set): Set of road indices.
            output_image_file (str): File path to save the image.
        """
        image = GeoUtil.convert_path_to_image(gdf, path, draw_background, image_size, path_color, path_width)
        output_dir = os.path.dirname(output_image_file)
        os.makedirs(output_dir, exist_ok=True)
        image.save(output_image_file, format="PNG")
