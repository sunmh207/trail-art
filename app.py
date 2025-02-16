import os

import geopandas as gpd

from utils.chinese_clip_encoder import ChineseClipEncoder
from utils.faiss_searcher import FaissSearcher
from utils.geo_util import GeoUtil
from utils.vector_util import VectorUtil


def map2images(shape_file: str, output_image_dir: str, max_length: int = 25000, min_length: int = 2000,
               max_groups_per_start: int = 50, max_rounds: int = 100):
    gdf = gpd.read_file(shape_file)
    gdf = gdf.to_crs(epsg=3857)

    types_filter = {"primary", "primary_link", "secondary", "secondary_link",
                    "tertiary", "unclassified", "cycleway"}

    filter_gdf = gdf[gdf["type"].isin(types_filter)]

    round_num = 0
    for start_index, row in filter_gdf.iterrows():
        round_num += 1
        if round_num > max_rounds:
            break
        all_paths = GeoUtil.find_all_connected_road_groups(gdf=gdf, start_index=start_index, max_length=max_length,
                                                           min_length=min_length, max_groups=max_groups_per_start,
                                                           types_filter=types_filter)
        if not all_paths:
            print("No paths found.")
            continue
        print(f"Found {len(all_paths)} paths.")

        output_dir = os.path.join(output_image_dir, str(start_index))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for idx, path in enumerate(all_paths):
            output_image_file = os.path.join(output_dir, f"connected_path_{idx + 1}.png")
            GeoUtil.save_path_to_image(gdf, path, output_image_file)

        print(f"Generated {len(all_paths)} images, saved to '{output_dir}' directory.")


def images2vector(image_folder: str, chinese_clip_encoder: ChineseClipEncoder, vector_index_path: str,
                  vector_meta_path: str):
    vector_util = VectorUtil(chinese_clip_encoder)

    vector_util.build_vector_db_recursive(image_folder, vector_index_path, vector_meta_path)


if __name__ == "__main__":
    shapefile = "data/map/planet-shp-hz-binjiang/shape/roads.shp"
    output_image_dir = "data/routes"
    vector_index_path = "data/faiss/image_vectors.index"
    vector_meta_path = "data/faiss/image_paths.pkl"

    clip_model_name = "models/chinese-clip-vit-base-patch16"
    chinese_clip_encoder = ChineseClipEncoder(model_name=clip_model_name)

    print("Please choose an option:")
    print("1: Traverse all paths on the map and save them as images.")
    print("2: Convert images into vectors and save them in the vector library.")
    print("3: Search similar images by text")
    choice = input("Enter your choice (1 or 2 or 3): ")

    if choice == "1":
        max_length: int = 25000
        min_length: int = 2000
        max_groups_per_start=50 # How many routes can be drawn at each starting point. In actual applications, it should be set larger, e.g. 100000
        max_rounds=100  # How many starting points can be traversed. In actual applications, it should be set larger, e.g. 100000
        map2images(shape_file=shapefile, output_image_dir=output_image_dir, max_length=max_length, min_length=min_length,
                   max_groups_per_start=max_groups_per_start, max_rounds=max_rounds)
    elif choice == "2":
        images2vector(image_folder=output_image_dir, chinese_clip_encoder=chinese_clip_encoder,
                      vector_index_path=vector_index_path, vector_meta_path=vector_meta_path)
    elif choice == "3":
        default_query = "number 4"
        query = input(f"Enter your prompt (default is'{default_query}'): ")
        if not query:
            query = default_query
        searcher = FaissSearcher(index_path=vector_index_path, meta_path=vector_meta_path,
                                 encoder=chinese_clip_encoder)
        results = searcher.search_similar_by_text(query_text=query, k=3)

        for image_path, distance in results:
            print(f"Image path: {image_path}, Distance: {distance}")

    else:
        print("Invalid choice.")
