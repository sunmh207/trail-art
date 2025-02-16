from transformers import ChineseCLIPProcessor, ChineseCLIPModel
import torch
import torch.nn.functional as F


class ChineseClipEncoder:
    """Encapsulates the text and image encoding functionality of the ChineseCLIP model."""

    def __init__(self, model_name="OFA-Sys/chinese-clip-vit-base-patch16"):
        """
        Initializes the ChineseCLIP model.
        :param model_name: Name of the pretrained model.
        """
        self.model = ChineseCLIPModel.from_pretrained(model_name)
        self.processor = ChineseCLIPProcessor.from_pretrained(model_name)

    def text_to_vector(self, text):
        """
        Converts text into a vector.
        :param text: Input text.
        :return: Normalized text feature vector (numpy array).
        """
        inputs = self.processor(text=[text], padding=True, return_tensors="pt")
        # with torch.no_grad():
        text_features = self.model.get_text_features(**inputs)
        text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)  # 归一化
        return text_features.detach().numpy().astype('float32')

    def image_to_vector(self, image):
        """
        Converts an image into a vector.
        :param image: PIL Image object.
        :return: Normalized image feature vector (numpy array).
        """
        image.convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt", padding=True)
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        image_features /= image_features.norm(dim=-1, keepdim=True)  # 归一化
        return image_features.cpu().numpy().astype('float32')

    def similarity(self, text: str, image: 'PIL.Image.Image'):
        """
        Computes the similarity score between text and image.
        :param text: Input text.
        :param image: PIL Image object.
        :return: Similarity score between text and image (float).
        """
        # Process image and text
        inputs = self.processor(text=[text], images=image, return_tensors="pt", padding=True)

        # Extract image and text features
        with torch.no_grad():
            image_features = self.model.get_image_features(
                **{k: v for k, v in inputs.items() if k.startswith("pixel_values")})
            text_features = self.model.get_text_features(
                **{k: v for k, v in inputs.items() if k.startswith("input_ids")})

        # Normalize feature vectors
        image_features = F.normalize(image_features, p=2, dim=-1)
        text_features = F.normalize(text_features, p=2, dim=-1)

        # Compute cosine similarity
        similarity = torch.matmul(image_features, text_features.T).item()

        return similarity
