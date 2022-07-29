import argparse
import json
import sys
import time
from pathlib import Path

from loguru import logger

from . import DynamicCover, __version__

CONFIG_PATH = Path.cwd() / "config.json"
SLEEP_SECONDS = 60


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
        "-c",
        "--config",
        type=Path,
        default=CONFIG_PATH,
        help=f"Абсолютный путь к конфиг-файлу (по умолчанию {CONFIG_PATH})"
    )
    parser.add_argument(
        "-s",
        "--sleep",
        type=int,
        default=SLEEP_SECONDS,
        help=f"Обновлять шапку каждые N секунд (по умолчанию {SLEEP_SECONDS})"
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
        Config path: {args.config}
        """
    )

    try:
        with args.config.open() as f:
            config: dict = json.load(f)
    except OSError as e:
        logger.error(e)
        sys.exit()

    dynamic_cover = DynamicCover(config=config)

    while True:
        dynamic_cover.update()
        time.sleep(args.sleep)

