from fastapi import FastAPI, Request, Cookie, Response, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, PlainTextResponse
from hashlib import sha512
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
import string
import base64
import sqlite3

app = FastAPI()
app.users = []
app.tokens = []
app.sessions = []
app.secret_key = '~td(0Rk}cf:[p6=%*#x75S6$)e?[&Idxjt&1}7f[!kdGZ1S{9W9up;&Lz&L1lYd'


class RegisterUser(BaseModel):
    name: str = ''
    surname: str = ''


@app.on_event("startup")
async def startup():
    app.db_conn = sqlite3.connect("northwind.db")
    app.db_conn.text_factory = lambda b: b.decode(errors="ignore")


@app.on_event("shutdown")
async def shutdown():
    app.db_conn.close()


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
def login_session(request: Request, response: Response):
    info = request.headers.get('Authorization').split()[1].encode()
    message = base64.b64decode(info).decode().split(':')

    login, password = message[0], message[1]
    if not (login == '4dm1n' and password == 'NotSoSecurePa$$'):
        return HTMLResponse(status_code=401)

    session_token = sha512(
        f'{"".join(random.choice(string.ascii_lowercase) for i in range(20))}{app.secret_key}'.encode()).hexdigest()
    if len(app.sessions) >= 3:
        app.sessions = app.sessions[1:]
    app.sessions.append(session_token)

    response.set_cookie(key='session_token', value=session_token)
    return {'message': 'Welcome!'}


@app.post('/login_token', status_code=201)
def login_session(request: Request, response: Response):
    info = request.headers.get('Authorization').split()[1].encode()
    message = base64.b64decode(info).decode().split(':')

    login, password = message[0], message[1]
    if not (login == '4dm1n' and password == 'NotSoSecurePa$$'):
        return HTMLResponse(status_code=401)

    session_token = sha512(
        f'{"".join(random.choice(string.ascii_lowercase) for i in range(20))}{app.secret_key}'.encode()).hexdigest()

    print(app.tokens)
    if len(app.tokens) >= 3:
        app.tokens = app.tokens[1:]
    app.tokens.append(session_token)
    print(app.tokens)

    return {'token': session_token}


@app.get('/welcome_session')
def welcome_session(format: str = Query('plain'), session_token: str = Cookie('')):
    if session_token not in app.sessions:
        return HTMLResponse(status_code=401)

    if format == 'json':
        return JSONResponse(content={'message': 'Welcome!'}, status_code=200)
    elif format == 'html':
        return HTMLResponse(content='<h1>Welcome!</h1>', status_code=200)
    else:
        return PlainTextResponse(content='Welcome!', status_code=200)


@app.get('/welcome_token')
def welcome_session(format: str = Query('plain'), token: str = Query('')):
    if token not in app.tokens:
        return HTMLResponse(status_code=401)

    if format == 'json':
        return JSONResponse(content={'message': 'Welcome!'}, status_code=200)
    elif format == 'html':
        return HTMLResponse(content='<h1>Welcome!</h1>', status_code=200)
    else:
        return PlainTextResponse(content='Welcome!', status_code=200)


@app.delete('/logout_session', status_code=302)
def welcome_session(format: str = Query('plain'), session_token: str = Cookie('')):
    if session_token not in app.sessions:
        return HTTPException(status_code=401)

    app.sessions.remove(session_token)
    return RedirectResponse(url=f'/logged_out?format={format}', status_code=302)


@app.delete('/logout_token', status_code=302)
def welcome_session(format: str = Query('plain'), token: str = Query('')):
    if token not in app.tokens:
        return HTTPException(status_code=401)

    app.tokens.remove(token)
    return RedirectResponse(url=f'/logged_out?format={format}', status_code=302)


@app.get('/logged_out')
def logged_out(format: str = Query('plain')):
    if format == 'json':
        return JSONResponse(content={"message": "Logged out!"}, status_code=200)
    elif format == 'html':
        return HTMLResponse(content='<h1>Logged out!</h1>')
    return PlainTextResponse(content='Logged out!')


@app.get('/categories')
async def categories():
    cursor = app.db_conn.cursor()
    categories = cursor.execute(
        'SELECT CategoryID, CategoryName from Categories').fetchall()
    return {
        'categories': [{'id': x[0], 'name': x[1]} for x in categories]
    }


@app.get('/customers')
async def customers():
    cursor = app.db_conn.cursor()
    customers = cursor.execute(
        'SELECT CustomerID, CompanyName, Address, PostalCode, City, Country from Customers').fetchall()
    return {
        'customers': [
            {
                'id': x[0],
                'name': x[1],
                'full_address': f'{x[2].strip()} {x[3].strip()} {x[4].strip()} {x[5].strip()}'
            } for x in customers
        ]
    }


@app.get('/products/{id}')
async def customers(id: int):
    cursor = app.db_conn.cursor()
    max_id = cursor.execute(
        'SELECT ProductID FROM Products ORDER BY ProductID DESC LIMIT 1').fetchone()[0]

    if id > max_id or id < 1:
        raise HTTPException(404)

    product = cursor.execute(
        'SELECT ProductID, ProductName FROM Products WHERE ProductId = ?', (id,)).fetchone()
    return {'id': product[0], 'name': product[1]}


@app.get('/employees')
async def employees(limit: int = Query(-1), offset: int = Query(0), order: str = Query('')):
    cursor = app.db_conn.cursor()
    base = 'SELECT EmployeeID, FirstName, LastName, City FROM Employees'
    if order in ['first_name', 'last_name', 'city']:
        base += f" ORDER BY {''.join([w[0].upper() + w[1:] for w in order.split('_')])}"
    elif order != '':
        raise HTTPException(400)
    base += f' LIMIT {limit} OFFSET {offset}'
    employees = cursor.execute(base).fetchall()
    return {
        'employees': [
            {
                'id': employee[0],
                'first_name': employee[1],
                'last_name': employee[2],
                'city': employee[3]
            }
            for employee in employees]
    }


@app.get('/products_extended')
async def products_ext():
    cursor = app.db_conn.cursor()
    products = cursor.execute(
        'SELECT ProductID, ProductName, Categories.CategoryName AS CategoryName, Suppliers.CompanyName AS CompanyName FROM Products JOIN Categories ON Products.CategoryID = Categories.CategoryID JOIN Suppliers ON Products.SupplierID = Suppliers.SupplierID').fetchall()
    return {
        'products_extended': [
            {
                'id': product[0],
                'name': product[1],
                'category': product[2],
                'supplier': product[3]
            }
            for product in products]
    }


@app.get('/products/{id}/orders')
async def orders(id: int):
    cursor = app.db_conn.cursor()

    max_id = cursor.execute(
        'SELECT ProductID FROM Products ORDER BY ProductID DESC LIMIT 1').fetchone()[0]

    if id > max_id or id < 1:
        raise HTTPException(404)

    orders = cursor.execute('SELECT od.OrderID, od.UnitPrice, od.Quantity, od.Discount, c.CompanyName FROM "Order Details" od JOIN Orders o ON od.OrderID = o.OrderID JOIN Customers c ON o.CustomerID = c.CustomerID WHERE od.ProductID = ?', (id,)).fetchall()
    return {
        'orders': [
            {
                'id': order[0],
                'customer': order[4],
                'quantity': order[2],
                'total_price': float("{:.2f}".format((order[1] * order[2]) - (order[3] * (order[1] * order[2]))))
            }
            for order in orders]
    }
