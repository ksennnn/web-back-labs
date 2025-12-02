from flask import Blueprint, render_template, request, make_response, redirect, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path

lab6 = Blueprint('lab6', __name__)

@lab6.route('/lab6/')
def main():
    return render_template('lab6/lab6.html')


def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
                host = '127.0.0.1',
                database = 'ksenia_kovalyova_knowledge_base',
                user = 'ksenia_kovalyova_knowledge_base',
                password = '140981'
            )
        cur = conn.cursor(cursor_factory= RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()


    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()


@lab6.route('/lab6/json-rpc-api/', methods=['POST'])
def api():
    data = request.json
    id = data['id']
    if data['method'] == 'info':
        conn, cur = db_connect()
        cur.execute("SELECT * FROM offices ORDER BY number")
        rows = cur.fetchall()
        if not rows:
            for i in range(1, 11):
                if current_app.config['DB_TYPE'] == 'postgres':
                    cur.execute("INSERT INTO offices (number, tenant, price) VALUES (%s, %s, %s)", (i, '', 900 + i % 3))
                else:
                    cur.execute("INSERT INTO offices (number, tenant, price) VALUES (?, ?, ?)", (i, '', 900 + i % 3))
            conn.commit()
            cur.execute("SELECT * FROM offices ORDER BY number")
            rows = cur.fetchall()

        offices = []
        for row in rows:
            office = {}
            office["number"] = row["number"]
            office["tenant"] = row["tenant"]
            office["price"] = row["price"]
            offices.append(office)

        db_close(conn, cur)

        return {
            'jsonrpc': '2.0',
            'result': offices,
            'id': id
        }
    login = session.get('login')
    if not login:
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': 1,
                'message': 'Unathorized'
            },
            'id':id
        }
    if data['method'] == 'booking':
        office_number = data['params']
        conn, cur = db_connect()
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute(f"SELECT tenant FROM offices WHERE number = %s;", (office_number,))
        else:
            cur.execute(f"SELECT tenant FROM offices WHERE number = ?;", (office_number,))
        office = cur.fetchone()
        if not office:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {'code': 4, 'message': 'Office not found'},
                'id': id
            }

        if office['tenant'] != '':
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {'code': 2, 'message': 'Already booked'},
                'id': id
            }
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute(f"UPDATE offices SET tenant = %s WHERE number = %s", (login, office_number))
        else:
            cur.execute(f"UPDATE offices SET tenant = ? WHERE number = ?", (login, office_number))

        db_close(conn, cur)

        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }
    
    if data['method'] == 'cancellation':
        office_number = data['params']
        conn, cur = db_connect()
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute(f"SELECT tenant FROM offices WHERE number = %s;", (office_number,))
        else:
            cur.execute(f"SELECT tenant FROM offices WHERE number = ?;", (office_number,))
        office = cur.fetchone()

        if not office:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {'code': 4, 'message': 'Office not found'},
                'id': id
            }
         
        if office['tenant'] == '':
            db_close(conn, cur)
            return {
                    'jsonrpc': '2.0',
                    'error': {
                    'code': 2,
                    'message': 'Not booked'
                },
                'id': id
            }
        if office['tenant'] != login:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 3,
                    'message': 'Cannot cancel someone else booking'
                },
                'id': id
            }
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE offices SET tenant = '' WHERE number = %s", (office_number,))
        else:
            cur.execute("UPDATE offices SET tenant = '' WHERE number = ?", (office_number,))

        db_close(conn, cur)
        return {
        'jsonrpc': '2.0',
        'result': 'success',
            'id': id
        }
    
    return {
            'jsonrpc': '2.0',
            'error': {
                'code': -32601,
                'message': 'Method not found'
            },
            'id': id
        }