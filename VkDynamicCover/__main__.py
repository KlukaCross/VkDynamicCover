import argparse
import json
import sys
import time
from pathlib import Path

from loguru import logger

from . import DynamicCover, __version__

MAIN_CONFIG_PATH = Path.cwd() / "main_config.json"
WIDGET_CONFIG_PATH = Path.cwd() / "widget_config.json"


def create_parser():
    parser = argparse.ArgumentParser(
        prog="VkDynamicCover",
        description="Program for dynamic updating cover of a group or a public in VK",
        epilog="(C) 2022 Oleg Mezenin\nReleased under the MIT License."
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"VkDynamicCover {__version__}"
    )
    parser.add_argument(
        "-m",
        "--main_config",
        type=Path,
        default=MAIN_CONFIG_PATH,
        help=f"Абсолютный путь к файлу с основными настройками (по умолчанию {MAIN_CONFIG_PATH})"
    )
    parser.add_argument(
        "-w",
        "--widget_config",
        type=Path,
        default=WIDGET_CONFIG_PATH,
        help=f"Абсолютный путь к файлу с описанием виджетов и их отображения (по умолчанию {WIDGET_CONFIG_PATH})"
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Режим отладки",
    )

    return parser


if __name__ == "__main__":
    args = create_parser().parse_args()

    logs_dir = args.config.parent.absolute() / "logs"

    if args.debug:
        logger.add(
            logs_dir / "log_{time}_DEBUG.log",
            level="DEBUG",
            backtrace=True,
            diagnose=True,
            rotation="daily",
            retention=2,
        )
    else:
        logger.remove()
        logger.add(
            logs_dir / "log_{time}_INFO.log",
            level="INFO",
            rotation="daily",
            retention="3 days",
            compression="zip",
        )

    logger.info("VkDynamicCover запущен")
    logger.debug(
        f"""
        Python {sys.version}
        VkDynamicCover {__version__}
        OS: {sys.platform}
        Main config path: {args.main_config}
        Widget config path: {args.widget_config}
        """
    )

    try:
        with args.main_config.open() as f:
            main_config: dict = json.load(f)
        with args.widget_config.open() as f:
            widget_config: dict = json.load(f)
    except OSError as e:
        logger.error(e)
        sys.exit()

    dynamic_cover = DynamicCover(main_config=main_config, widget_config=widget_config)
    dynamic_cover.start()

