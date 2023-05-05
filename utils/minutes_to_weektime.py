import random, math
from pydantic.dataclasses import dataclass
from prisma.enums import DayOfWeek
from app.utils.comparedatetime import inttoweekday


@dataclass
class WeekTime:
    weekday: DayOfWeek
    hour: int
    minute: int


WEEK_IN_MINUTES = 10_080
DAY_IN_MINUTES  = 1440
HOUR_IN_MINUTES = 60

def minutes_to_weektime(minutes: int):
    '''
    Converts minutes from the beginning of the week, to a WeekTime object
    0 -> monday 00:00
    '''
    day = math.floor(minutes / 1440)
    if day > 6:
        return None
    hour = (minutes - (DAY_IN_MINUTES * day)) // HOUR_IN_MINUTES
    minute = (minutes - (DAY_IN_MINUTES * day) - (HOUR_IN_MINUTES * hour))

    return WeekTime(weekday=inttoweekday(day), hour=hour, minute=minute)
