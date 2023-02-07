import datetime
import math
import typing

from loguru import logger

from VkDynamicCover.types import Interval

MONTHS_RUS = ("январь", "февраль", "март", "апрель", "май", "июнь", "июль",
              "август", "сентябрь", "октябрь", "ноябрь", "декабрь")

MONTHS_RUS_R = ("января", "февраля", "марта", "апреля", "мая", "июня", "июля",
                "августа", "сентября", "октября", "ноября", "декабря")

WEEKS_RUS = ("понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье")


class _TimeTools:

    @staticmethod
    def format_time(dtime: datetime.datetime) -> typing.Dict[str, int]:
        day_z = "{:02d}".format(dtime.day)
        month_z = "{:02d}".format(dtime.month)
        hour_z = "{:02d}".format(dtime.hour)
        minute_z = "{:02d}".format(dtime.minute)
        second_z = "{:02d}".format(dtime.second)
        return {"year": dtime.year,
                "month": dtime.month,
                "month_rus": MONTHS_RUS[dtime.month - 1],
                "month_rus_r": MONTHS_RUS_R[dtime.month - 1],
                "week": dtime.isoweekday(),
                "week_rus": WEEKS_RUS[dtime.weekday()],
                "day": dtime.day,
                "hour": dtime.hour,
                "minute": dtime.minute,
                "second": dtime.second,
                "day_z": day_z,
                "month_z": month_z,
                "hour_z": hour_z,
                "minute_z": minute_z,
                "second_z": second_z}

    @staticmethod
    def shift_time(dtime: datetime.datetime, shift: dict) -> datetime.datetime:
        dtime += datetime.timedelta(weeks=shift["week"],
                                    days=shift["day"],
                                    hours=shift["hour"],
                                    minutes=shift["minute"],
                                    seconds=shift["second"])

        dtime = dtime.replace(year=dtime.year + shift["year"] + math.trunc((dtime.month + shift["month"] - 1) / 12),
                            month=(dtime.month + shift["month"] - 1) % 12 + 1)
        return dtime

    @staticmethod
    def get_shift_and_format_time(shift, dtime=None) -> typing.Dict[str, int]:
        if not dtime:
            dtime = datetime.datetime.now()
        dtime = TimeTools.shift_time(dtime, shift)
        return TimeTools.format_time(dtime)

    @staticmethod
    def set_default_shift(shift: dict):
        shift.setdefault("year", 0)
        shift.setdefault("month", 0)
        shift.setdefault("week", 0)
        shift.setdefault("day", 0)
        shift.setdefault("hour", 0)
        shift.setdefault("minute", 0)
        shift.setdefault("second", 0)

    @staticmethod
    def get_period_interval(period: str) -> (int, int):
        tmp = datetime.datetime.now()
        if period == "day":
            fr = tmp.replace(hour=0, minute=0, second=0)
            to = datetime.timedelta(days=1) + fr
        elif period == "week":
            fr = tmp.replace(hour=0, minute=0, second=0) - datetime.timedelta(days=tmp.weekday())
            to = datetime.timedelta(days=7) + fr
        elif period == "month":
            fr = tmp.replace(day=1, hour=0, minute=0, second=0)
            to = fr.replace(year=fr.year + 1, month=1) if fr.month == 12 else fr.replace(month=fr.month + 1)
        elif period == "year":
            fr = tmp.replace(month=1, day=1, hour=0, minute=0, second=0)
            to = fr.replace(year=fr.year + 1)
        else:
            logger.warning(f"Неизвестный период - {period}")
            fr = to = 0
        return Interval(int(fr.timestamp()), int(to.timestamp()))


TimeTools = _TimeTools()
