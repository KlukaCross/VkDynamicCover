import random

from PIL import Image, ImageFont, ImageDraw
import io
from pathlib import Path

from urllib import request
from loguru import logger


def create_surface(width: int, height: int) -> Image:
    return Image.new("RGBA", (width, height))


def draw_image(surface: Image, img: Image, shift: (int, int) = (0, 0)) -> Image:
    surf_buf = Image.new("RGBA", surface.size)
    surf_buf.paste(img, shift)
    return Image.alpha_composite(surface, surf_buf)


def draw_text(surface: Image,
              text: str,
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
            logger.warning(f"Не удалось загрузить шрифт - {e}")
            font = ImageFont.load_default()

    draw_obj = ImageDraw.Draw(surface)
    draw_obj.text(xy=xy, text=text, fill=fill, font=font, anchor=anchor, spacing=spacing, direction=direction,
                  stroke_width=stroke_width, stroke_fill=stroke_fill)


def get_byte_image(surface: Image) -> bytes:
    img_bytes = io.BytesIO()
    surface.save(img_bytes, format="PNG")
    return img_bytes.getvalue()


def get_image_from_url(url: str) -> Image:
    return Image.open(request.urlopen(url))


def get_image_from_path(path: Path) -> Image:
    return Image.open(path.absolute())


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


def get_random_image_from_dir(path: Path, rand_func=lambda count: random.randint(0, count - 1)) -> Image:
    if not path.is_dir():
        logger.warning(f"{path} не является директорией")
        return
    lst = list(filter(lambda x: x.suffix in [".png", ".jpg", ".jpeg", ".gif"], path.glob("*.*")))
    rand_c = rand_func(len(lst))
    rand_pic_path = lst[rand_c]
    return get_image_from_path(rand_pic_path)

