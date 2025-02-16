import faiss
import pickle
from PIL import Image

from utils.chinese_clip_encoder import ChineseClipEncoder


class FaissSearcher:
    """Encapsulates the Faiss index search logic."""

    def __init__(self, index_path: str, meta_path: str, encoder: ChineseClipEncoder):
        """
        Initializes FaissSearcher, loads the Faiss index and metadata.
        :param index_path: Path to the Faiss index file.
        :param meta_path: Path to the image path metadata file.
        :param encoder: Instance of ChineseClipEncoder for text and image vectorization.
        """
        self.index_path = index_path
        self.meta_path = meta_path
        self.encoder = encoder  # ChineseCLIP 编码器实例
        self.index = None
        self.image_paths = None

        self.load_index()
        self.load_metadata()

    def load_index(self):
        print("Loading Faiss index...")
        self.index = faiss.read_index(self.index_path)

    def load_metadata(self):
        print("Loading metadata...")
        with open(self.meta_path, 'rb') as f:
            self.image_paths = pickle.load(f)

    def search_similar_by_text(self, query_text, k=5):
        """
        Searches for the most similar images based on the query text.
        :param query_text: Query text.
        :param k: Number of most similar images to return.
        :return: List of the most similar image paths and their distances.
        """
        query_vector = self.encoder.text_to_vector(query_text)
        return self._search(query_vector, k)

    def search_similar_by_image(self, image: Image, k=5):
        """
        Searches for the most similar images based on the query image.
        :param image: PIL Image object.
        :param k: Number of most similar images to return.
        :return: List of the most similar image paths and their distances.
        """
        query_vector = self.encoder.image_to_vector(image)
        return self._search(query_vector, k)

    def _search(self, query_vector, k):
        """
        Executes the Faiss search.
        :param query_vector: Query vector.
        :param k: Number of nearest neighbors to return.
        :return: List of the most similar image paths and their corresponding distances.
        """
        similarity, indices = self.index.search(query_vector, k)
        results = [(self.image_paths[indices[0][i]], similarity[0][i]) for i in range(k)]
        return results
