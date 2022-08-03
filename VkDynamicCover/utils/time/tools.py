import datetime

MONTHS_RUS = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль",
              "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]

MONTHS_RUS_R = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля",
                "августа", "сентября", "октября", "ноября", "декабря"]

WEEKS_RUS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]


def format_time(time: datetime.datetime, text) -> str:
    text = text \
        .replace("{month}", "{month:0>2}") \
        .replace("{day}", "{day:0>2}") \
        .replace("{hour}", "{hour:0>2}") \
        .replace("{minute}", "{minute:0>2}") \
        .replace("{second}", "{second:0>2}")

    return text.format(year=time.year,
                       month=time.month,
                       month_rus=MONTHS_RUS[time.month - 1],
                       month_rus_r=MONTHS_RUS_R[time.month - 1],
                       week=time.isoweekday(),
                       week_rus=WEEKS_RUS[time.weekday()],
                       day=time.day,
                       hour=time.hour,
                       minute=time.minute,
                       second=time.second)
