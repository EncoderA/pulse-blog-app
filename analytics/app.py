from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title='Analytics Service')

class HealthResponse(BaseModel):
    status: str

@app.get('/health', response_model=HealthResponse)
async def health():
    return {'status': 'ok'}

@app.get('/')
async def root():
    return {'message': 'Analytics FastAPI service is running'}
