import datetime
import math


class TimeTools:
    MONTHS_RUS = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль",
                  "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]

    MONTHS_RUS_R = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля",
                    "августа", "сентября", "октября", "ноября", "декабря"]

    WEEKS_RUS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]

    @staticmethod
    def format_time(dtime: datetime.datetime, text) -> str:
        text = text \
            .replace("{month_z}", "{month_z:0>2}") \
            .replace("{day_z}", "{day_z:0>2}") \
            .replace("{hour_z}", "{hour_z:0>2}") \
            .replace("{minute_z}", "{minute_z:0>2}") \
            .replace("{second_z}", "{second_z:0>2}")

        return text.format(year=dtime.year,
                           month=dtime.month,
                           month_rus=TimeTools.MONTHS_RUS[dtime.month - 1],
                           month_rus_r=TimeTools.MONTHS_RUS_R[dtime.month - 1],
                           week=dtime.isoweekday(),
                           week_rus=TimeTools.WEEKS_RUS[dtime.weekday()],
                           day=dtime.day,
                           hour=dtime.hour,
                           minute=dtime.minute,
                           second=dtime.second,
                           day_z=dtime.day,
                           month_z=dtime.month,
                           hour_z=dtime.hour,
                           minute_z=dtime.minute,
                           second_z=dtime.second)

    @staticmethod
    def shift_time(dtime: datetime.datetime, shift: dict) -> datetime:
        dtime += datetime.timedelta(weeks=shift["week"],
                                    days=shift["day"],
                                    hours=shift["hour"],
                                    minutes=shift["minute"],
                                    seconds=shift["second"])

        dtime = dtime.replace(year=dtime.year + shift["year"] + math.trunc((dtime.month + shift["month"]) / 12),
                              month=(dtime.month + shift["month"]) % 12)
        return dtime


time = TimeTools()
