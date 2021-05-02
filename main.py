from fastapi import FastAPI, Request, Cookie, Response, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, PlainTextResponse
from hashlib import sha512
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
import string

app = FastAPI()
app.users = []
app.tokens = []
app.sessions = []
app.secret_key = '~td(0Rk}cf:[p6=%*#x75S6$)e?[&Idxjt&1}7f[!kdGZ1S{9W9up;&Lz&L1lYd'


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
def register(user: RegisterUser):
    id = len(app.users) + 1
    register_date = datetime.today()

    diff = 0
    for c in user.name:
        if c.isalpha():
            diff += 1

    for c in user.surname:
        if c.isalpha():
            diff += 1

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


@app.get('/hello')
def hello():
    return HTMLResponse(content=f'<h1>Hello! Today date is {datetime.today().strftime("%Y-%m-%d")}</h1>')


@app.post('/login_session', status_code=201)
def login_session(login: str, password: str, response: Response):
    if not (login == '4dm1n' and password == 'NotSoSecurePa$$'):
        return HTTPException(status_code=401)

    session_token = sha512(
        f'{"".join(random.choice(string.ascii_lowercase) for i in range(20))}{app.secret_key}'.encode()).hexdigest()
    if len(app.sessions) >= 3:
        app.sessions = app.sessions[1:]
    app.sessions.append(session_token)

    response.set_cookie(key='session_token', value=session_token)
    return {'message': 'Welcome!'}


@app.post('/login_token', status_code=201)
def login_session(login: str, password: str, response: Response):
    if not (login == '4dm1n' and password == 'NotSoSecurePa$$'):
        return HTTPException(status_code=401)

    session_token = sha512(
        f'{"".join(random.choice(string.ascii_lowercase) for i in range(20))}{app.secret_key}'.encode()).hexdigest()

    if len(app.tokens) >= 3:
        app.tokens = app.tokens[1:]
    app.tokens.append(session_token)

    return {'token': session_token}


@app.get('/welcome_session', status_code=200)
def welcome_session(format: str = Query('plain'), session_token: str = Cookie(None)):
    if session_token not in app.sessions:
        return HTTPException(status_code=401)

    if format == 'json':
        return JSONResponse(content={'message': 'Welcome!'})
    elif format == 'html':
        return HTMLResponse(content='<h1>Welcome!</h1>')
    else:
        return PlainTextResponse(content='Welcome!')


@app.get('/welcome_token', status_code=200)
def welcome_session(format: str = Query('plain'), tokens: str = Query('')):
    if tokens not in app.tokens:
        return HTTPException(status_code=401)

    if format == 'json':
        return JSONResponse(content={'message': 'Welcome!'})
    elif format == 'html':
        return HTMLResponse(content='<h1>Welcome!</h1>')
    else:
        return PlainTextResponse(content='Welcome!')


@app.delete('/logout_session', status_code=302)
def welcome_session(format: str = Query('plain'), session_token: str = Cookie(None)):
    if session_token not in app.sessions:
        return HTTPException(status_code=401)

    app.sessions.remove(session_token)
    return RedirectResponse(url=f'/logged_out?format={format}', status_code=302)


@app.delete('/logout_token', status_code=302)
def welcome_session(format: str = Query('plain'), tokens: str = Query('')):
    if tokens not in app.tokens:
        return HTTPException(status_code=401)

    app.tokens.remove(tokens)
    return RedirectResponse(url=f'/logged_out?format={format}', status_code=302)


@app.get('/logged_out')
def logged_out(format: str = Query('plain')):
    if format == 'json':
        return JSONResponse(content={"message": "Logged out!"}, status_code=200)
    elif format == 'html':
        return HTMLResponse(content='<h1>Logged out!</h1>')
    return PlainTextResponse(content='Logged out!')
