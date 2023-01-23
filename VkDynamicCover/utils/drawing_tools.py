import random
import typing

from PIL import Image, ImageFont, ImageDraw
import io
from pathlib import Path

from urllib import request
from loguru import logger


class DrawingTools:
    @staticmethod
    def create_surface(width: int, height: int) -> Image:
        return Image.new("RGBA", (width, height))

    @staticmethod
    def clear(surface: Image):
        draw = ImageDraw.Draw(surface)
        draw.rectangle([(0, 0), surface.size], fill="white")

    @staticmethod
    def draw_image(surface: Image, img: Image, shift: (int, int) = (0, 0)) -> Image:
        surf_buf = Image.new("RGBA", surface.size)
        surf_buf.paste(img, shift)
        return Image.alpha_composite(surface, surf_buf)

    @staticmethod
    def draw_text(surface: Image,
                  text: str = None,
                  font_name: str = None, font_size: int = 10,
                  fill: str = None,
                  xy: (int, int) = (0, 0),
                  anchor: str = None,
                  spacing: int = 4,
                  direction: str = None,
                  stroke_width: int = 0,
                  stroke_fill: str = None):
        if not font_name:
            font = ImageFont.load_default()
        else:
            try:
                font = ImageFont.truetype(font=font_name, size=font_size, encoding='UTF-8')
            except Exception as e:
                logger.warning(f"Не удалось загрузить шрифт {font_name} - {e}")
                font = ImageFont.load_default()

        draw_obj = ImageDraw.Draw(surface)
        draw_obj.text(xy=xy, text=text, fill=fill, font=font, anchor=anchor, spacing=spacing, direction=direction,
                      stroke_width=stroke_width, stroke_fill=stroke_fill)

    @staticmethod
    def get_text_size(text: str, font_name: str, font_size: int) -> tuple:
        font = ImageFont.truetype(font=font_name, size=font_size, encoding='UTF-8')
        return font.getsize(text)

    @staticmethod
    def get_bytesio_image(surface: Image) -> io.BytesIO:
        img_bytes = io.BytesIO()
        surface.save(img_bytes, format='png')
        img_bytes.seek(0)
        return img_bytes

    @staticmethod
    def get_image_from_url(url: str) -> Image:
        try:
            f = request.urlopen(url)
            return Image.open(f)
        except Exception as e:
            logger.warning(f"Не удалось загрузить фото: {e}")

    @staticmethod
    def get_image_from_path(path: Path) -> Image:
        return Image.open(path.absolute())

    @staticmethod
    def get_resized_image(image: Image, resize: (int or str, int or str)) -> Image:
        if resize[0] == "auto" and resize[1] == "auto":
            return image

        if resize[0] != "auto" and resize[1] == "auto":
            k = resize[0] / image.width
            return image.resize((resize[0], int(image.height * k)))

        if resize[0] == "auto" and resize[1] != "auto":
            k = resize[1] / image.height
            return image.resize((int(image.width * k), resize[1]))

        return image.resize(resize)

    @staticmethod
    def get_random_image_from_dir(path: Path, rand_func: typing.Callable[[int, dict], int], **kwargs) -> Image:
        if not path.is_dir():
            logger.warning(f"{path} не является директорией")
            return
        lst = list(filter(lambda x: x.suffix in [".png", ".jpg", ".jpeg", ".gif"], path.glob("*.*")))
        rand_c = rand_func(len(lst), **kwargs)
        rand_pic_path = lst[rand_c%len(lst)+1]
        return DrawingTools.get_image_from_path(rand_pic_path)

    @staticmethod
    def save_image(image: Image, name: str):
        image.save(name, "PNG")

    @staticmethod
    def show_image(image: Image):
        image.show()


DrawTools = DrawingTools()
