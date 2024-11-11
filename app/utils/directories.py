# app/utils/utils.py

import sys
from pathlib import Path


def get_project_root() -> Path:
    """
    Obtiene la ruta del directorio raíz del proyecto.
    Si es un ejecutable (.exe), ajusta la ruta apropiadamente.
    """
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)  # PyInstaller usa _MEIPASS como el directorio temporal del ejecutable
    else:
        return Path(__file__).resolve().parents[2]

def get_lang_dir() -> Path:
    project_root = get_project_root()
    lang_dir = project_root / 'lang'
    lang_dir.mkdir(parents=True, exist_ok=True)
    return lang_dir

def get_data_dir() -> Path:
    project_root = get_project_root()
    data_dir = project_root / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def get_projects_dir() -> Path:
    project_root = get_project_root()
    projects_dir = project_root / 'Proyectos'
    projects_dir.mkdir(parents=True, exist_ok=True)
    return projects_dir

def get_tmp_dir() -> Path:
    project_root = get_project_root()
    tmp_dir = project_root / 'tmp'
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return tmp_dir

def get_save_dir() -> Path:
    project_root = get_project_root()
    save_dir = project_root / 'Proyectos'
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir

def get_extra_dir() -> Path:
    project_root = get_project_root()
    extra_dir = project_root / 'app' / 'extra'
    extra_dir.mkdir(parents=True, exist_ok=True)
    return extra_dir

def get_videos_dir() -> Path:
    project_root = get_project_root()
    videos_dir = project_root / 'includes' / 'videos'
    videos_dir.mkdir(parents=True, exist_ok=True)
    return videos_dir


def get_images_dir() -> Path:
    project_root = get_project_root()
    images_dir = project_root / 'includes' / 'images'
    images_dir.mkdir(parents=True, exist_ok=True)
    return images_dir
