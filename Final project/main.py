from fastapi import FastAPI
from location_service import get_nearest_stations
from message_service import send_message
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Pydantic models
class UserLocation(BaseModel):
    latitude: float
    longitude: float

class MessageRequest(BaseModel):
    message: str
    phones: List[str]

@app.post("/nearest_stations/")
async def nearest_stations(user_location: UserLocation):
    user_coords = (user_location.latitude, user_location.longitude)
    nearest = get_nearest_stations(user_coords)
    return {"nearest_stations": nearest}

@app.post("/send_message/")
async def send_message_to_stations(req: MessageRequest):
    results = []
    for phone in req.phones:
        result = send_message(phone, req.message)
        results.append(result)
    return {"results": results}
