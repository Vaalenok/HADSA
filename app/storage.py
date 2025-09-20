import asyncio
import hashlib
import logging
import mimetypes
import os
import shutil
import uuid
from pathlib import Path
from app.db.models import File
import app.db.api as api
from app.embedder import embed_text
import pickle


FILE_TYPES = {
    "text": [
        "txt", "md", "rst", "log", "ini", "cfg", "conf", "yaml", "yml", "json", "toml", "csv", "tsv", "org", "wiki",
        "py", "js", "ts", "jsx", "tsx", "java", "c", "cpp", "h", "hpp", "cs", "go", "rs", "swift", "kt", "php", "rb",
        "pl", "sh", "bat", "ps1", "sql", "r", "jl", "scala", "vb", "css", "scss", "sass", "less"
    ],
    "marking": [ # TODO: beautifulsoup4
        "html", "htm", "xhtml", "xml", "tex"
    ],
    "jupiter": [ # TODO: json.load() и собрать cell["source"]
        "ipynb"
    ],
    "word": [ # TODO: python-docx
        "docx", "doc"
    ],
    "powerpoint": [ # TODO: python-pptx
        "ppt", "pptx"
    ],
    "excel": [ # TODO: openpyxl
        "xlsx", "xls"
    ],
    "opendocument": [ # TODO: odfpy
        "odt", "ods", "odp"
    ],
    "pdf": [ # TODO: PyPDF2
        "pdf"
    ]
}

BASE_PATH= "data/files"


def create_file_hash(data: bytes) -> str:
    """
    Создаёт хэш для файла
    :param data: содержание файла
    :return: хэш файла
    """
    return hashlib.sha256(data).hexdigest()


def can_embed(_type: str) -> bool:
    """
    Проверяет, можно ли создать эмбеддинг для данного типа файла
    :param _type: тип файла
    :return: bool
    """
    _type = _type.lower()
    text_types = [_type for key in FILE_TYPES.keys() for _type in FILE_TYPES[key]]

    return _type in text_types


def get_file_data(doc: File | str):
    """
    Возвращает содержимое файла по объекту в базе данных
    :param doc: объект данных файла
    :return: искомый файл
    """
    if isinstance(doc, File):
        path = doc.path
        ext = doc.type
    else:
        path = doc
        ext = doc.split("/")[-1].split(".")[1]

    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл не найден: {path}")

    if ext in FILE_TYPES["text"]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def file_list():
    """
    Возвращает список всех файлов
    :return: список файлов
    """
    docs = asyncio.run(api.get_all())
    return docs


def save_file(file: str | bytes | bytearray, name: str = None, _type: str = None):
    """
    Сохраняет файл в хранилище.

    :param file: Путь к файлу (str) или bytes-объект
    :param name: Опционально (если None - возьмёт из пути или сгенерирует UUID)
    :param _type: Опционально (если None - определит по расширению или MIME)
    :return: ORM объект базы данных, сохранённые данные документа
    """
    if isinstance(file, str):
        if not os.path.isfile(file):
            raise FileNotFoundError(f"Файл {file} не найден")

        name = name or os.path.basename(file)
        path = Path(os.path.join(BASE_PATH, name)).as_posix()

        shutil.copy2(file, path)
        size = os.path.getsize(path)

        with open(path, "rb") as f:
            data_bytes = f.read()

    elif isinstance(file, (bytes, bytearray)):
        name = name or f"{uuid.uuid4().hex}.bin"
        path = Path(os.path.join(BASE_PATH, name)).as_posix()

        with open(path, "wb") as f:
            f.write(file)

        size = len(file)

        data_bytes = file

    else:
        raise TypeError("Файл или путь до файла передан неверно")

    _type = _type or Path(name).suffix.lstrip(".")

    if not _type:
        mime, _ = mimetypes.guess_type(name)

        if mime:
            _type = mime.split("/")[-1]
        else:
            _type = "bin"

    _hash = create_file_hash(data_bytes)
    existing = asyncio.run(api.is_unique(_hash))

    if existing:
        logging.warning(f"Файл {name} уже загружен")  # TODO: на фронт
        return

    emb = None

    if can_embed(_type):
        emb = embed_text(get_file_data(path))

    doc = File(
        name=name.split(".")[0],
        path=path,
        type=_type,
        size=size,
        hash=_hash,
        embedding=emb
    )

    r_doc = asyncio.run(api.add(doc))
    return r_doc
