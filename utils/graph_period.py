import enum


class GraphPeriod(enum.Enum):
    past_hour = "past_hour"
    past_12_hours = "past_12_hours"
    past_day = "past_day"
    past_15_days = "past_15_days"
    past_month = "past_30_days"
    past_6_months = "past_6_months"
    past_year = "past_year"
    all_time = "all_time"
