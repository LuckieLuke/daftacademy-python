from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from hashlib import sha512
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI()
app.users = []


class RegisterUser(BaseModel):
    name: str = ''
    surname: str = ''


@app.get('/')
def root():
    return {'message': 'Hello world!'}


@app.get('/method')
@app.post('/method')
@app.delete('/method')
@app.put('/method')
@app.options('/method')
def get_method(request: Request):
    code = 200 if request.method != 'POST' else 201
    return JSONResponse(content={'method': request.method}, status_code=code)


@app.get('/auth')
async def auth(password: str = '', password_hash: str = ''):
    if password == '' or password_hash == '':
        return JSONResponse(status_code=401)
    code = 204 if sha512(
        password.encode()).hexdigest() == password_hash else 401
    return JSONResponse(status_code=code)


@app.post('/register')
async def register(user: RegisterUser):
    id = len(app.users) + 1
    register_date = datetime.today()
    diff = len(user.name) + len(user.surname)
    vacc_date = register_date + timedelta(days=diff)
    register_date = register_date.strftime('%Y-%m-%d')
    vacc_date = vacc_date.strftime('%Y-%m-%d')
    app.users.append({
        'id': id,
        'name': user.name,
        'surname': user.surname,
        'register_date': register_date,
        'vaccination_date': vacc_date
    })
    return JSONResponse(content=app.users[id-1], status_code=201)


@app.get('/patient/{id}')
def patient(id: int):
    if id < 1:
        return JSONResponse(status_code=400)
    if id > len(app.users):
        return JSONResponse(status_code=404)
    return JSONResponse(content=app.users[id-1], status_code=200)
