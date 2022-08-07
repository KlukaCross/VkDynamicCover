import datetime
import math

MONTHS_RUS = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль",
              "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]

MONTHS_RUS_R = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля",
                "августа", "сентября", "октября", "ноября", "декабря"]

WEEKS_RUS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]


def format_time(time: datetime.datetime, text) -> str:
    text = text \
        .replace("{month_z}", "{month_z:0>2}") \
        .replace("{day_z}", "{day_z:0>2}") \
        .replace("{hour_z}", "{hour_z:0>2}") \
        .replace("{minute_z}", "{minute_z:0>2}") \
        .replace("{second_z}", "{second_z:0>2}")

    return text.format(year=time.year,
                       month=time.month,
                       month_rus=MONTHS_RUS[time.month - 1],
                       month_rus_r=MONTHS_RUS_R[time.month - 1],
                       week=time.isoweekday(),
                       week_rus=WEEKS_RUS[time.weekday()],
                       day=time.day,
                       hour=time.hour,
                       minute=time.minute,
                       second=time.second,
                       day_z=time.day,
                       month_z=time.month,
                       hour_z=time.hour,
                       minute_z=time.minute,
                       second_z=time.second)


def shift_time(time: datetime.datetime, shift: dict) -> datetime:
    time += datetime.timedelta(weeks=shift["week"],
                               days=shift["day"],
                               hours=shift["hour"],
                               minutes=shift["minute"],
                               seconds=shift["second"])

    time = time.replace(year=time.year + shift["year"] + math.trunc((time.month + shift["month"]) / 12),
                        month=(time.month + shift["month"]) % 12)
    return time
