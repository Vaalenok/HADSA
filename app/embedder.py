import pickle
from sentence_transformers import SentenceTransformer


MODEL = SentenceTransformer("intfloat/e5-base-v2")


def embed_text(text: str):
    """
    Создаёт embedding для строки текста
    :param text: текст
    :return: embedding
    """
    return pickle.dumps(MODEL.encode(text).tolist())
