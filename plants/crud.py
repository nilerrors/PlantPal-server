import random
from prisma.errors import UniqueViolationError as PrismaUniqueViolationError
import pygal, pygal.style
import datetime
from app.auth.crud import get_user_by_email
from app.utils.graph_period import GraphPeriod
from app.utils.comparedatetime import filter_timestamps, filter_periodstamps
from app.utils.minutes_to_weektime import minutes_to_weektime
from app.prisma import prisma
import app.auth as auth
from . import schemas


charts_style = pygal.style.Style(
    background='transparent',
    plot_background='transparent',
    foreground='#bbb',
    foreground_strong='#fff',
    foreground_subtle='#bbb',
    opacity='.4',
    opacity_hover='.9',
    transition='400ms ease-in',
    colors=('#E853A0', '#E8537A', '#E95355', '#E87653', '#E89B53')
)


async def get_plant_by_chip_id(plant_id: str, chip_id: str):
    return await prisma.plant.find_first(where={
        'id': plant_id,
        'chip_id': chip_id
    },
    include={
        'user': True
    })


async def get_plant_by_id(user_email: str, plant_id: str):
    user = await auth.crud.get_user_by_email(user_email)
    if user is None:
        return None

    return await prisma.plant.find_first(where={
        'id': plant_id,
        'user_id': user.id
    },
    include={
        'user': True
    })


async def get_plant(user_email: str, plant_id: str):
    plant = await get_plant_by_id(user_email, plant_id)
    if plant is None or plant.user is None:
        return None
    return plant


async def get_plant_timestamps(user_email: str, plant_id: str):
    plant = await get_plant_by_id(user_email, plant_id)
    if plant is None:
        return None

    return await prisma.plant.find_first(where={
        'id': plant.id,
    },
    include={
        'user': True,
        'timestamps': True
    })


async def add_plant_timestamp(user_email: str, plant_id: str, timestamp: schemas.TimeStampAdd):
    plant = await get_plant_by_id(user_email, plant_id)
    if plant is None:
        return None
    
    if await prisma.timestamp.find_first(where={
        'day_of_week': timestamp.day_of_week,
        'hour': timestamp.hour,
        'minute': timestamp.minute,
        'plant_id': plant.id
    }) is not None:
        return "already exists"

    return await prisma.timestamp.create({
        'day_of_week': timestamp.day_of_week,
        'hour': timestamp.hour,
        'minute': timestamp.minute,
        'plant_id': plant.id
    })


async def remove_plant_all_timestamps(user_email: str, plant_id: str):
    plant = await get_plant_by_id(user_email, plant_id)
    if plant is None:
        return None

    return await prisma.timestamp.delete_many(where={
        'plant_id': plant.id
    })


async def remove_plant_timestamp(user_email: str, plant_id: str, timestamp_id: str):
    plant = await get_plant_by_id(user_email, plant_id)
    if plant is None:
        return None

    return await prisma.timestamp.delete_many(where={
        'id': timestamp_id,
        'plant_id': plant_id
    })


async def get_plant_periodstamps(user_email: str, plant_id: str):
    plant = await get_plant_by_id(user_email, plant_id)
    if plant is None:
        return None

    return await prisma.plant.find_first(where={
        'id': plant.id,
    },
    include={
        'user': True,
        'periodstamps': True
    })


async def change_plant_periodstamps(user_email: str, plant_id: str, periodstamp: schemas.PeriodStampsChange):
    plant = await get_plant_by_id(user_email, plant_id)
    if plant is None:
        return None

    plant = await prisma.plant.update({
        'periodstamp_times_a_week': periodstamp.times_a_week
    },
    {'id': plant.id,})
    if plant is None:
        return None

    await prisma.periodstamp.delete_many(where={
        'plant_id': plant.id
    })
    if periodstamp.times_a_week != 0:
        WEEK_IN_MINUTES = 10_080
        irrigation_delay = WEEK_IN_MINUTES // periodstamp.times_a_week
        periods = [
            minutes_to_weektime(
                ((irrigation_delay * m) + random.randint(0, 10)) if irrigation_delay * m < WEEK_IN_MINUTES else WEEK_IN_MINUTES
            ) for m in range(periodstamp.times_a_week)
        ]
        return await prisma.periodstamp.create_many(data=[
            {
                'plant_id': plant.id,
                'day_of_week': p.weekday,
                'hour': p.hour,
                'minute': p.minute
            }
            for p in periods if p is not None
        ])

    return 0


async def get_plant_times(user_email: str, plant_id: str):
    plant = await get_plant_by_id(user_email, plant_id)
    if plant is None:
        return None

    plant_data = await prisma.plant.find_first(where={
        'id': plant.id,
        'user_id': plant.user_id
    },
    include={
        'user': True,
        'timestamps': plant.irrigation_type == 'time',
        'periodstamps': plant.irrigation_type == 'period',
    })
    if plant_data is None:
        return None

    if plant.irrigation_type == 'time':
        return {
            **plant_data.dict(),
            'times': plant_data.timestamps
        }
    
    return {
        **plant_data.dict(),
        'times': plant_data.periodstamps
    }


async def get_plant_today_times(plant_id: str, chip_id: str):
    plant = await get_plant_by_chip_id(plant_id, chip_id)
    if plant is None or plant.user is None:
        return None

    plant_data = await prisma.plant.find_first(where={
        'id': plant.id,
        'user_id': plant.user_id
    },
    include={
        'user': True,
        'timestamps': filter_timestamps(plant.irrigation_type == 'time'),
        'periodstamps': filter_periodstamps(plant.irrigation_type == 'period'),
    })
    if plant_data is None:
        return None
    

    if plant.irrigation_type == 'time':
        return plant_data.timestamps

    return plant_data.periodstamps



async def get_plant_today_next_time(plant_id: str, chip_id: str):
    times = await get_plant_today_times(plant_id, chip_id)
    if times is None:
        return None
    
    return times[0]


async def get_should_irrigate_now(plant_id: str, chip_id: str):
    plant = await get_plant_by_chip_id(plant_id, chip_id)
    if plant is None:
        return None
    time = await get_plant_today_next_time(plant_id, chip_id)
    if time is None:
        return None
    
    moisture = await prisma.moisturepercentagerecord.find_first(where={
        'plant': {
            'is': {
                'id': plant_id,
                'chip_id': chip_id
            }
        }
    },
    order={
        'at': 'desc'
    })
    
    now = datetime.datetime.now()
    threshold = plant.moisture_percentage_treshold
    if moisture is None:
        return time.hour == now.hour and time.minute == now.minute
    elif plant.auto_irrigation and moisture.percentage <= threshold:
        return True
    elif moisture.percentage <= threshold:
        return time.hour == now.hour and time.minute == now.minute

    return False


async def get_plant_irrigation_graph(user_email: str, plant_id: str):
    plant = await get_plant_by_id(user_email, plant_id)
    if plant is None:
        return None
    
    irrigation_records = await prisma.irrigationrecord.find_many(where={
        'plant_id': plant.id
    })

    if len(irrigation_records) == 0:
        return False

    records = list(map(
        lambda r: {
            'x': r.at.strftime('%Y-%m-%d %H:%M:%S'),
            'y': r.water_amount
        },
        irrigation_records
    ))

    graph = pygal.Bar(
        title="Irrigations",
        width = 1000,
        height = 600,
        show_legend=False,
        explicit_size = True,
        style = charts_style,
    )
    graph.x_labels = list(map(lambda r: r['x'], records))
    graph.y_labels = list(range(0, 101, 5))
    graph.add(f'Irrigations', list(map(lambda r: r['y'], records)))
    graph.x_labels_major_count = 10
    graph.show_minor_x_labels = False

    return graph.render()


async def get_moisture_percentage_graph(user_email: str, plant_id: str, graph_period: GraphPeriod):
    plant = await get_plant_by_id(user_email, plant_id)
    if plant is None:
        return None
    
    moisture_record = await prisma.moisturepercentagerecord.find_many(where={
        'plant_id': plant.id
    })

    if len(moisture_record) == 0:
        return False

    time_format = '%Y-%m-%d %H:%M:%S'
    if graph_period in (GraphPeriod.past_hour, GraphPeriod.past_12_hours, GraphPeriod.past_day):
        time_format = '%H:%M:%S'

    records = list(map(
        lambda r: {
            'x': r.at.strftime(time_format),
            'y': r.percentage
        },
        moisture_record
    ))

    graph = pygal.Bar(
        title="Moisture Percentage",
        width = 1000,
        height = 600,
        show_legend=False,
        explicit_size = True,
        style = charts_style,
    )
    graph.x_labels = list(map(lambda r: r['x'], records))
    graph.y_labels = list(range(0, 101, 5))
    graph.add(f'Moisture Percentage', list(map(lambda r: r['y'], records)))
    graph.x_labels_major_count = 10
    graph.show_minor_x_labels = False

    return graph.render()


async def get_current_moisture(user_email: str, plant_id: str):
    plant = await get_plant_by_id(user_email, plant_id)
    if plant is None:
        return False

    return await prisma.moisturepercentagerecord.find_first(where={
        'plant_id': plant.id
    },
    order={
        'at': 'desc'
    })


async def register_current_moisture(percentage: int, plant: schemas.PlantESPGet):
    _plant = await get_plant_by_chip_id(plant.plant_id, plant.chip_id)
    if _plant is None:
        return None

    return await prisma.moisturepercentagerecord.create(data={
        'plant_id': _plant.id,
        'percentage': percentage
    })


async def get_plants(user_email: str):
    user = await auth.crud.get_user_by_email(user_email)
    if user is None:
        return None

    return await prisma.plant.find_many(where={
        'user_id': user.id,
    })


async def create_plant(plant: schemas.PlantCreate):
    user = await auth.crud.get_user_by_email_password(plant.email, plant.password)
    if user is None:
        return None
    
    try:
        created_plant = await prisma.plant.create(data={
            'user_id': user.id,
            'chip_id': plant.chip_id
        })
    except PrismaUniqueViolationError:
        return "chipid exists"

    return created_plant


async def update_plant(user_email: str, plant_id: str, plant: schemas.PlantUpdate):
    _plant = await get_plant_by_id(user_email, plant_id)
    if _plant is None:
        return None
    
    user = await get_user_by_email(user_email)
    user_id = _plant.user_id

    if user is None or user_id != user.id:
        return
    
    # Update periodstamp
    if plant.periodstamp_times_a_week != _plant.periodstamp_times_a_week:
        await prisma.periodstamp.delete_many(where={
            'plant_id': _plant.id
        })
        if plant.periodstamp_times_a_week != 0:
            WEEK_IN_MINUTES = 10_080
            irrigation_delay = WEEK_IN_MINUTES // plant.periodstamp_times_a_week
            periods = [
                minutes_to_weektime(
                    ((irrigation_delay * m) + random.randint(0, 10)) if irrigation_delay * m < WEEK_IN_MINUTES else WEEK_IN_MINUTES
                ) for m in range(plant.periodstamp_times_a_week)
            ]
            await prisma.periodstamp.create_many(data=[
                {
                    'plant_id': _plant.id,
                    'day_of_week': p.weekday,
                    'hour': p.hour,
                    'minute': p.minute
                }
                for p in periods if p is not None
            ])
        
    
    return await prisma.plant.update(data={
        'name': plant.name,
        'water_amount': plant.water_amount,
        'auto_irrigation': plant.auto_irrigation,
        'irrigation_type': plant.irrigation_type,
        'moisture_percentage_treshold': plant.moisture_percentage_treshold,
        'periodstamp_times_a_week': plant.periodstamp_times_a_week,
        'user': {
            'connect': {
                'id': user_id
            }
        }
    },
    where={
        'id': _plant.id,
    },
    include={
        'user': True
    })

async def delete_plant(user_email: str, plant_id: str):
    db_plant = await get_plant_by_id(user_email, plant_id)
    if db_plant is None:
        return False
    
    deleted_plant = await prisma.plant.delete(where={
        'id': db_plant.id
    })

    return deleted_plant is not None


async def irrigate_plant(irrigation: schemas.PlantIrrigation):
    plant = await get_plant_by_chip_id(irrigation.plant_id, irrigation.chip_id)
    if plant is None:
        return False

    plant_irrigation = await prisma.irrigationrecord.create(data={
        'plant_id': plant.id,
        'water_amount': plant.water_amount
    })

    return plant_irrigation is not None
