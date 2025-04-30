import datetime
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI(title="Smart City on MongoDB")

# ————— Return 400 on validation errors —————
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": exc.errors()})

# ————— MongoDB connection —————
MONGO_URI = (
    "mongodb+srv://readelabanushi:vuqasqlt8vAXenQl"
    "@smartcity.zgufqv5.mongodb.net/smartcity"
    "?retryWrites=true&w=majority&appName=smartcity"
)
client    = AsyncIOMotorClient(MONGO_URI)
db        = client.smartcity  # database name

# ————— Shared location model —————
class Location(BaseModel):
    latitude: float
    longitude: float

# ————— Pydantic + endpoint for each collection —————

# 1) Traffic
class TrafficIn(BaseModel):
    sensor_id: str
    timestamp: datetime.datetime
    location: Location
    vehicle_count: int
    average_speed: float
    congestion_level: int

@app.post("/traffic", status_code=201)
async def ingest_traffic(data: TrafficIn):
    doc = data.dict()
    loc = doc.pop("location")
    doc["latitude"], doc["longitude"] = loc["latitude"], loc["longitude"]
    res = await db.traffic.insert_one(doc)
    return {"id": str(res.inserted_id)}

@app.get("/traffic")
async def get_traffic():
    out = []
    cursor = db.traffic.find()
    async for r in cursor:
        out.append({
            "sensor_id":        r["sensor_id"],
            "timestamp":        r["timestamp"].isoformat(),
            "location":         {"latitude": r["latitude"], "longitude": r["longitude"]},
            "vehicle_count":    r["vehicle_count"],
            "average_speed":    r["average_speed"],
            "congestion_level": r["congestion_level"],
        })
    return out

# 2) Parking
class ParkingIn(BaseModel):
    lot_id: str
    timestamp: datetime.datetime
    location: Location
    available_spaces: int
    total_spaces: int
    occupancy_rate: float

@app.post("/parking", status_code=201)
async def ingest_parking(data: ParkingIn):
    doc = data.dict(); loc = doc.pop("location")
    doc["latitude"], doc["longitude"] = loc["latitude"], loc["longitude"]
    res = await db.parking.insert_one(doc)
    return {"id": str(res.inserted_id)}

@app.get("/parking")
async def get_parking():
    out = []
    cursor = db.parking.find()
    async for r in cursor:
        out.append({
            "lot_id":           r["lot_id"],
            "timestamp":        r["timestamp"].isoformat(),
            "location":         {"latitude": r["latitude"], "longitude": r["longitude"]},
            "available_spaces": r["available_spaces"],
            "total_spaces":     r["total_spaces"],
            "occupancy_rate":   r["occupancy_rate"],
        })
    return out

# 3) Air Quality
class AirQualityIn(BaseModel):
    sensor_id: str
    timestamp: datetime.datetime
    location: Location
    aqi: int
    temperature: float
    humidity: float

@app.post("/air-quality", status_code=201)
async def ingest_air(data: AirQualityIn):
    doc = data.dict(); loc = doc.pop("location")
    doc["latitude"], doc["longitude"] = loc["latitude"], loc["longitude"]
    res = await db.air_quality.insert_one(doc)
    return {"id": str(res.inserted_id)}

@app.get("/air-quality")
async def get_air():
    out = []
    cursor = db.air_quality.find()
    async for r in cursor:
        out.append({
            "sensor_id":  r["sensor_id"],
            "timestamp":  r["timestamp"].isoformat(),
            "location":   {"latitude": r["latitude"], "longitude": r["longitude"]},
            "aqi":        r["aqi"],
            "temperature":r["temperature"],
            "humidity":   r["humidity"],
        })
    return out

# 4) Lighting
class LightingIn(BaseModel):
    light_id: str
    timestamp: datetime.datetime
    location: Location
    status: str
    brightness_level: int
    power_consumption: float

@app.post("/lighting", status_code=201)
async def ingest_light(data: LightingIn):
    doc = data.dict(); loc = doc.pop("location")
    doc["latitude"], doc["longitude"] = loc["latitude"], loc["longitude"]
    res = await db.lighting.insert_one(doc)
    return {"id": str(res.inserted_id)}

@app.get("/lighting")
async def get_light():
    out = []
    cursor = db.lighting.find()
    async for r in cursor:
        out.append({
            "light_id":        r["light_id"],
            "timestamp":       r["timestamp"].isoformat(),
            "location":        {"latitude": r["latitude"], "longitude": r["longitude"]},
            "status":          r["status"],
            "brightness_level":r["brightness_level"],
            "power_consumption":r["power_consumption"],
        })
    return out

# 5) Waste Management
class WasteIn(BaseModel):
    container_id: str
    timestamp: datetime.datetime
    location: Location
    waste_type: str
    fill_level: float
    collection_priority: int

@app.post("/waste", status_code=201)
async def ingest_waste(data: WasteIn):
    doc = data.dict(); loc = doc.pop("location")
    doc["latitude"], doc["longitude"] = loc["latitude"], loc["longitude"]
    res = await db.waste.insert_one(doc)
    return {"id": str(res.inserted_id)}

@app.get("/waste")
async def get_waste():
    out = []
    cursor = db.waste.find()
    async for r in cursor:
        out.append({
            "container_id":  r["container_id"],
            "timestamp":     r["timestamp"].isoformat(),
            "location":      {"latitude": r["latitude"], "longitude": r["longitude"]},
            "waste_type":    r["waste_type"],
            "fill_level":    r["fill_level"],
            "collection_priority": r["collection_priority"],
        })
    return out

# 6) Public Transport
class TransitIn(BaseModel):
    vehicle_id: str
    timestamp: datetime.datetime
    location: Location
    route_id: str
    vehicle_type: str
    passenger_count: int

@app.post("/transit", status_code=201)
async def ingest_transit(data: TransitIn):
    doc = data.dict(); loc = doc.pop("location")
    doc["latitude"], doc["longitude"] = loc["latitude"], loc["longitude"]
    res = await db.transit.insert_one(doc)
    return {"id": str(res.inserted_id)}

@app.get("/transit")
async def get_transit():
    out = []
    cursor = db.transit.find()
    async for r in cursor:
        out.append({
            "vehicle_id":    r["vehicle_id"],
            "timestamp":     r["timestamp"].isoformat(),
            "location":      {"latitude": r["latitude"], "longitude": r["longitude"]},
            "route_id":      r["route_id"],
            "vehicle_type":  r["vehicle_type"],
            "passenger_count": r["passenger_count"],
        })
    return out
