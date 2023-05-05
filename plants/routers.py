from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi_jwt_auth import AuthJWT
from . import crud, schemas
from app.utils.graph_period import GraphPeriod


router = APIRouter(prefix="/plants")


@router.get('/', response_model=list[schemas.PlantResponseSmall])
async def get_plants(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    user_email = Authorize.get_jwt_subject()
    user_plants = await crud.get_plants(user_email)

    return user_plants


@router.get('/{plant_id}', response_model=schemas.PlantResponse)
async def get_plant(plant_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    user_email = Authorize.get_jwt_subject()
    plant_data = await crud.get_plant_by_id(user_email, plant_id)

    if plant_data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return plant_data


@router.post('/espget', response_model=schemas.PlantResponse)
async def get_plant_esp(plant: schemas.PlantESPGet):
    plant_data = await crud.get_plant_by_chip_id(plant.plant_id, plant.chip_id)

    if plant_data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return plant_data


@router.post('/should_irrigate_now')
async def get_should_irrigate_now(plant: schemas.PlantESPGet):
    should_irrigate = await crud.get_should_irrigate_now(plant.plant_id, plant.chip_id)

    if should_irrigate is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No irrigations found for today")

    return {"irrigate":should_irrigate}


@router.post('/today_next_irrigation_time', response_model=List[schemas.TimeStamp])
async def get_plant_today_next_time(plant: schemas.PlantESPGet):
    plant_data = await crud.get_plant_today_next_time(plant.plant_id, plant.chip_id)

    if plant_data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return plant_data


@router.post('/today_irrigation_times', response_model=List[schemas.TimeStamp])
async def get_plant_today_times(plant: schemas.PlantESPGet):
    plant_data = await crud.get_plant_today_times(plant.plant_id, plant.chip_id)

    if plant_data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return plant_data


@router.get('/{plant_id}/times', response_model=schemas.PlantWithIrrigationStampsResponse)
async def get_plant_times(plant_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    user_email = Authorize.get_jwt_subject()
    plant_data = await crud.get_plant_times(user_email, plant_id)

    if plant_data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return plant_data


@router.get('/{plant_id}/timestamps', response_model=schemas.PlantWithTimeStampsResponse)
async def get_plant_timestamps(plant_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    user_email = Authorize.get_jwt_subject()
    plant_data = await crud.get_plant_timestamps(user_email, plant_id)

    if plant_data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return plant_data


@router.post('/{plant_id}/timestamps', response_model=schemas.TimeStamp)
async def add_plant_timestamp(plant_id: str, timestamp: schemas.TimeStampAdd, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    user_email = Authorize.get_jwt_subject()
    plant_data = await crud.add_plant_timestamp(user_email, plant_id, timestamp)

    if type(plant_data) == str and plant_data == 'already exists':
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Timestamp already exists")
    if plant_data is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Plant with given id not found")

    return plant_data


@router.delete('/{plant_id}/timestamps')
async def remove_plant_all_timestamps(plant_id: str, timestamp_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    user_email = Authorize.get_jwt_subject()
    plant_data = await crud.remove_plant_all_timestamps(user_email, plant_id)

    if plant_data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return {'message': 'Successfully deleted'}


@router.delete('/{plant_id}/timestamps/{timestamp_id}')
async def remove_plant_timestamp(plant_id: str, timestamp_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    user_email = Authorize.get_jwt_subject()
    plant_data = await crud.remove_plant_timestamp(user_email, plant_id, timestamp_id)

    if plant_data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return {'message': 'Successfully deleted'}


@router.get('/{plant_id}/periodstamps', response_model=schemas.PlantWithPeriodStampsResponse)
async def get_plant_periodstamps(plant_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    user_email = Authorize.get_jwt_subject()
    plant_data = await crud.get_plant_periodstamps(user_email, plant_id)

    if plant_data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return plant_data


@router.post('/{plant_id}/periodstamps')
async def change_plant_periodstamps(plant_id: str, periodstamp: schemas.PeriodStampsChange, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    user_email = Authorize.get_jwt_subject()
    plant_data = await crud.change_plant_periodstamps(user_email, plant_id, periodstamp)

    if plant_data is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Plant with given id not found")

    return {"amount_of_irrigations_per_week": plant_data}


@router.get('/{plant_id}/irrigations_graph.svg')
async def get_plant_irrigations_graph(plant_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    user_email = Authorize.get_jwt_subject()
    svg = await crud.get_plant_irrigation_graph(user_email, plant_id)

    if type(svg) == bool and not svg:
        raise HTTPException(status.HTTP_204_NO_CONTENT, "No irrigation data")

    if svg is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return Response(svg, media_type='image/svg+xml')


@router.get('/{plant_id}/moisture_percentage_graph.svg')
async def get_moisture_percentage_graph(plant_id: str, p: GraphPeriod = GraphPeriod.all_time, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    user_email = Authorize.get_jwt_subject()
    svg = await crud.get_moisture_percentage_graph(user_email, plant_id, p)

    if type(svg) == bool and not svg:
        raise HTTPException(status.HTTP_204_NO_CONTENT, "No moisture data")

    if svg is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return Response(svg, media_type='image/svg+xml')


@router.get('/{plant_id}/current_moisture')
async def get_current_moisture(plant_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    user_email = Authorize.get_jwt_subject()
    current_moisture = await crud.get_current_moisture(user_email, plant_id)
    if type(current_moisture) == bool and not current_moisture:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return {"current_moisture":current_moisture}


@router.get('/{plant_id}/current_moisture_chart.svg')
async def get_current_moisture_chart(plant_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    user_email = Authorize.get_jwt_subject()
    current_moisture = await crud.get_current_moisture_chart(user_email, plant_id)
    if type(current_moisture) == bool and not current_moisture:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return {"current_moisture":current_moisture}


@router.post('/current_moisture/{percentage}')
async def set_current_moisture(percentage: int, plant: schemas.PlantESPGet):
    if not (0 < percentage < 100):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Percentage should be in range(0, 100)")
    current_moisture = await crud.register_current_moisture(percentage, plant)
    if current_moisture is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return {"current_moisture":current_moisture}


@router.post("/")
async def create_plant(plant: schemas.PlantCreate):
    created_plant = await crud.create_plant(plant)
    
    if created_plant is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User email and password do not correspond")
    elif created_plant == 'chipid exists':
        raise HTTPException(status.HTTP_409_CONFLICT, "ESP with given Chip ID already exists")

    return created_plant.dict()


@router.put("/{plant_id}", response_model=schemas.PlantResponse)
async def update_plant(plant_id: str, plant: schemas.PlantUpdate, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    user_email = Authorize.get_jwt_subject()
    updated_plant = await crud.update_plant(user_email, plant_id, plant)

    if not updated_plant:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return updated_plant


@router.delete("/{plant_id}")
async def delete_plant(plant_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    user_email = Authorize.get_jwt_subject()
    plant_deleted = await crud.delete_plant(user_email, plant_id)

    if not plant_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id not found")

    return {'message': 'Plant deleted'}


@router.post("/irrigate")
async def plant_irrigation(irrigation: schemas.PlantIrrigation):
    plant_irrigated = await crud.irrigate_plant(irrigation)
    if not plant_irrigated:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Plant with given id and Chip ID not found")
    
    return {'message': 'Plant irrigated'}
