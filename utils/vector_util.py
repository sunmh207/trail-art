import os
import pickle

import faiss
import numpy as np
from PIL import Image

from utils.chinese_clip_encoder import ChineseClipEncoder


class VectorUtil:
    def __init__(self, chinese_clip_encoder: ChineseClipEncoder):
        self.chinese_clip_encoder = chinese_clip_encoder

    def build_vector_db(self, image_folder, index_path="image_vectors.index", meta_path="image_paths.pkl"):
        """Process all images in the folder and build a vector database"""
        image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder)
                       if f.lower().endswith(('png', 'jpg', 'jpeg'))]

        print(f"Processing {len(image_paths)} images...")
        vectors = []
        for path in image_paths:
            vec = self.chinese_clip_encoder.image_to_vector(Image.open(path))
            vectors.append(vec)

        # Create FAISS index
        vectors = np.vstack(vectors)
        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)  # Use inner product to calculate similarity
        index.add(vectors)

        # Save index and metadata
        faiss.write_index(index, index_path)
        with open(meta_path, "wb") as f:
            pickle.dump(image_paths, f)
        print(f"Database built with {index.ntotal} vectors")

    def build_vector_db_recursive(self, image_folder, index_path="image_vectors.index", meta_path="image_paths.pkl"):
        """Recursively process each subdirectory in the folder and insert into the vector database one by one"""
        if os.path.exists(index_path):
            index = faiss.read_index(index_path)
            with open(meta_path, "rb") as f:
                image_paths = pickle.load(f)
        else:
            dim = 512  # Assuming the vector dimension is 512, adjust based on image_to_vector output
            index = faiss.IndexFlatIP(dim)  # Use inner product to calculate similarity
            image_paths = []

        # Traverse directories and recursively process each leaf directory
        for root, dirs, files in os.walk(image_folder):
            # If it's a leaf directory (no subdirectories), start processing images in this directory
            if not dirs:
                vectors = []
                current_image_paths = []
                for file in files:
                    if file.lower().endswith(('png', 'jpg', 'jpeg')):
                        image_path = os.path.join(root, file)
                        vec = self.chinese_clip_encoder.image_to_vector(Image.open(image_path))
                        vectors.append(vec)
                        current_image_paths.append(image_path)

                # If there are images in this directory, add vectors to the index
                if vectors:
                    vectors_array = np.vstack(vectors)
                    index.add(vectors_array)
                    image_paths.extend(current_image_paths)
                    print(f"Inserted {len(vectors)} vectors from {root}.")

        # Save the final index and image paths to files
        faiss.write_index(index, index_path)
        with open(meta_path, "wb") as f:
            pickle.dump(image_paths, f)
        print(f"Database built with {index.ntotal} vectors")
