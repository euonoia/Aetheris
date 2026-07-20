"""Thumbnail generation and cache for the Dataset Quality Inspector."""

from concurrent.futures import ThreadPoolExecutor, Future
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image
import customtkinter as ctk


class ThumbnailCache:
    def __init__(self, size: Tuple[int, int] = (140, 90), max_workers: int = 4) -> None:
        self.size = size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.cache: Dict[Path, ctk.CTkImage] = {}
        self.futures: Dict[Path, Future] = {}

    def _create_thumbnail(self, image_path: Path) -> Optional[ctk.CTkImage]:
        try:
            with Image.open(image_path) as image:
                image.thumbnail(self.size, Image.Resampling.LANCZOS)
                thumbnail = image.convert("RGB")
                return ctk.CTkImage(light_image=thumbnail, size=self.size)
        except Exception:
            return None

    def get_thumbnail(self, image_path: Path) -> Optional[ctk.CTkImage]:
        if image_path in self.cache:
            return self.cache[image_path]

        try:
            thumbnail = self._create_thumbnail(image_path)
            if thumbnail is not None:
                self.cache[image_path] = thumbnail
            return thumbnail
        except Exception:
            return None

    def preload(self, image_paths: Tuple[Path, ...]) -> None:
        for image_path in image_paths:
            if image_path not in self.cache and image_path not in self.futures:
                self.futures[image_path] = self.executor.submit(self._create_thumbnail, image_path)

        for image_path, future in list(self.futures.items()):
            if future.done():
                thumbnail = future.result()
                if thumbnail is not None:
                    self.cache[image_path] = thumbnail
                del self.futures[image_path]
