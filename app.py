# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 17:51:55 2021

@author: Memofy - Insan Kamil
"""

# library for server
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_api import status

# library for database connection
import pymysql.cursors

# library for others
import datetime

# ============================================================================
#                                   DATABASE
# ============================================================================
#   Database Configuration
#
DB_SERVER = "localhost"
DB_USERNAME = "root"
DB_PASSWORD = ""
DB_NAME = "bug_tracking_system"
#
# ============================================================================


# ============================================================================
#                                 KONFIGURASI
# ============================================================================

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["APPLICATION_ROOT"] = "/api/v1"

DEFAULT_ROOT = '/api/v1'

conn = cursor = None

def open_DB():
    global conn, cursor
    
    conn = pymysql.connect(DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

def close_DB():
    global conn, cursor
    
    conn.close()
    cursor.close()

# ===========================================================================
#                             MINI DOCUMENTATION
# ===========================================================================
#
#   Client Error Code
#   400 -> Bad Request              HTTP_400_BAD_REQUEST
#   401 -> Unauthorized             HTTP_401_UNAUTHORIZED
#   403 -> Forbidden                HTTP_403_FORBIDDEN
#   404 -> Not Found                HTTP_404_NOT_FOUND
#   405 -> Method Not Allowed       HTTP_405_METHOD_NOT_ALLOWED
#   406 -> Not Acceptable           HTTP_406_NOT_ACCEPTABLE
# 
#   Server Error Code
#   500 -> Internal Server Error    HTTP_500_INTERNAL_SERVER_ERROR
#   501 -> Not Implemented          HTTP_500_NOT_IMPLEMENTED
#   502 -> Bad Gateway              HTTP_502_BAD_GATEWAY
#   503 -> Service Unavailable      HTTP_503_SERVICE_UNAVAILABLE
#   504 -> Gateway Timeout          HTTP_504_GATEWAY_TIMEOUT
#
#   Success Code
#   200 -> OK                       HTTP_200_OK
#   201 -> Created                  HTTP_201_CREATED
#   202 -> Accepted                 HTTP_202_ACCEPTED
#   204 -> No Content               HTTP_204_NO_CONTENT
#
# ===========================================================================

# ===========================================================================
#                                HELPER FUNCTION
# ===========================================================================

def get_last_data(table):
    open_DB()
    sql = "SELECT * FROM " + str(table) + " ORDER BY id DESC LIMIT 1"
    
    cursor.execute(sql)
    response = cursor.fetchone()
    
    close_DB()
    
    return response

def get_last_id(table):
    open_DB()
    sql = "SELECT * FROM " + str(table) + " ORDER BY id DESC LIMIT 1"
    
    cursor.execute(sql)
    data = cursor.fetchone()
    
    close_DB()
    
    response = {'id': data[0]}
    
    return response

# ===========================================================================
#                                   BATAS SUCI
# ===========================================================================

@cross_origin()
@app.route(DEFAULT_ROOT + '/', methods=['POST', 'GET'])
def index():
    
    message = "Request Salah"
    code = status.HTTP_405_METHOD_NOT_ALLOWED
    
    if request.method == 'POST':
        user_request = request.get_json()
        
        message = user_request['nama']
        code = status.HTTP_200_OK
        
        print(user_request)
    else:
        message = "BTS API Versi Alpha"
        code = status.HTTP_200_OK
    
    result = {"data": message}
    
    return jsonify(result), code


# *************************
# USERS THINGS
# *************************

@cross_origin()
@app.route(DEFAULT_ROOT + '/users', methods=['POST', 'GET', 'PUT', 'DELETE'])
@app.route(DEFAULT_ROOT + '/user/<id>', methods=['GET'])
@app.route(DEFAULT_ROOT + '/user/<id>/activate', methods=['PATCH'])
def users(id = 0):
    open_DB()
    
    container = []
    error = []
    meta = {}
    code = ''
    
    if id != 0:
        if request.method == 'GET':
            sql = "SELECT users.id, users.username, users.nama_pengguna, users.nomor_hp, users.email, roles.nama as role, users.is_active as active, users.created_at, users.updated_at FROM users JOIN roles ON users.role_id = roles.id WHERE users.id=%s"
            val = (id)
            cursor.execute(sql, val)
            userdata = cursor.fetchone()            
            close_DB()
            
            if userdata:
                temp = {
                    'id': userdata[0],
                    'username': userdata[1],
                    'nama_pengguna': userdata[2],
                    'nomor_hp': userdata[3],
                    'email': userdata[4],
                    'role': userdata[5],
                    'active': userdata[6],
                    'created_at': userdata[7],
                    'updated_at': userdata[8]
                }
                
                container = temp
                code = status.HTTP_200_OK
            else:
                code = status.HTTP_204_NO_CONTENT
        
        elif request.method == 'PATCH':
            
            last_data = get_last_data('users')
            
            activate = not last_data[7] # 7 is index for is_activate in table users
            
            sql = "UDPATE users SET is_activate=%s WHERE id=%s"
            val = (activate, id)
            
            cursor.execute(sql, val)
            conn.commit()
            
            code = status.HTTP_202_ACCEPTED
        
        else:     
            message = "Request Not Allowed"
            error.append(message)
            code = status.HTTP_405_METHOD_NOT_ALLOWED
    
    else:
        if request.method == 'GET':
            sql = "SELECT users.id, users.username, users.nama_pengguna, users.nomor_hp, users.email, roles.nama as role, users.is_active as active users.created_at, users.updated_at FROM users JOIN roles ON users.role_id = roles.id"
            cursor.execute(sql)
            res = cursor.fetchall()
            close_DB()
            
            userdata = list()
            
            for r in res:
                temp = {
                    'id': r[0],
                    'username': r[1],
                    'nama_pengguna': r[2],
                    'nomor_hp': r[3],
                    'email': r[4],
                    'role': r[5],
                    'active': r[6],
                    'created_at': r[7],
                    'updated_at': r[8]
                }
                
                userdata.append(temp)
                
            if len(userdata) > 0:
                container = userdata
                code = status.HTTP_200_OK
            else:
                code = status.HTTP_204_NO_CONTENT
            
        elif request.method == 'POST':
            userdata = request.get_json()
            
            username = userdata['username']
            password = userdata['password']
            nama_pengguna = userdata['nama_pengguna']
            nomor_hp = userdata['nomor_hp']
            email = userdata['email']
            role_id = userdata['role_id']
            is_active = 1
            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()
            
            sql = "INSERT INTO users VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (username, password, nama_pengguna, nomor_hp, email, role_id, is_active, created_at, updated_at)
            
            cursor.execute(sql, val)
            conn.commit()
            close_DB()
            
            code = status.HTTP_201_CREATED
            
        elif request.method == 'PUT':
            userdata = request.get_json()
            
            user_id = userdata['id']
            
            username = userdata['username']
            nama_pengguna = userdata['nama_pengguna']
            nomor_hp = userdata['nomor_hp']
            email = userdata['email']
            role_id = userdata['role_id']
            is_active = userdata['is_active']
            
            updated_at = datetime.datetime.now()
            
            sql = "UPDATE users SET username=%s, nama_pengguna=%s, nomor_hp=%s, email=%s, role_id=%s, is_active=%s WHERE id=%s"
            val = (username, nama_pengguna, nomor_hp, email, role_id, is_active, user_id)
            
            cursor.execute(sql, val)
            conn.commit()
            close_DB()
            
            code = status.HTTP_202_ACCEPTED
            
        elif request.method == 'DELETE':
            userdata = request.get_json()
            
            user_id = userdata['id']
            
            sql = "DELETE FROM users WHERE id=%s"
            val = (user_id)
            
            cursor.execute(sql, val)
            conn.commit()
            close_DB()
            
            code = status.HTTP_202_ACCEPTED
        
    meta = {'copyright': 'Copyright 2021 Memofy Dev'}
        
    result = {'code': code, 'data': container, 'errors': error, 'meta': meta}
    
    return jsonify(result), code


@cross_origin()
@app.route(DEFAULT_ROOT + '/roles', methods=['GET'])
@app.route(DEFAULT_ROOT + '/role/<id>', methods=['GET'])
def roles(id = 0):
    open_DB()
    
    container = []
    error = []
    meta = {}
    code = ''
    
    if request.method != 'GET':
        message = "Request Not Allowed"
        error.append(message)
            
        code = status.HTTP_405_METHOD_NOT_ALLOWED
    else:
        if id == 0:    
            if request.method == 'GET':
                roles_data = list()
                
                sql = "SELECT roles.id, roles.nama FROM roles"
                cursor.execute(sql)
                
                res = cursor.fetchall()
                close_DB()
                
                for r in res:
                    temp = {
                        'id': r[0],
                        'nama': r[1]
                    }
                    
                    roles_data.append(temp)
                    
                if len(roles_data) > 0:
                    container = roles_data
                    code = status.HTTP_200_OK
                else:
                    code = status.HTTP_204_NO_CONTENT
        
        else:
            if request.method == 'GET':
                sql = "SELECT roles.id, roles.nama FROM roles WHERE id=%s"
                val = (id)
                
                cursor.execute(sql, val)
                
                roles_data = cursor.fetchone()
                close_DB()
                
                if roles_data:
                    temp = {
                        'id': roles_data[0],
                        'nama': roles_data[1]
                    }
                    
                    container = temp
                    code = status.HTTP_200_OK
                else:
                    code = status.HTTP_204_NO_CONTENT

    meta = {'copyright': 'Copyright 2021 Memofy Dev'}
        
    result = {'code': code, 'data': container, 'errors': error, 'meta': meta}
    
    return jsonify(result), code
    
# *************************
# END OF USERS THINGS
# *************************


# *************************
# PROJECTS THINGS
# *************************

@cross_origin()
@app.route(DEFAULT_ROOT + '/projects', methods=['POST', 'GET', 'PUT', 'DELETE'])
@app.route(DEFAULT_ROOT + '/project/<id>', methods=['GET'])
def projects(id = 0):
    open_DB()
    
    container = []
    error = []
    meta = {}
    code = ''
    
    if id != 0:
        if request.method == 'GET':
            sql = "SELECT projects.id, projects.judul, users.username as owner, projects.tanggal_mulai, projects.tanggal_akhir, projects.keterangan, projects.created_at, projects.updated_at FROM projects JOIN users ON projects.owner_id = users.id WHERE projects.id=%s"
            val = (id)
            cursor.execute(sql, val)
            projects_data = cursor.fetchone()            
            close_DB()
            
            if projects_data:
                temp = {
                    'id': projects_data[0],
                    'judul': projects_data[1],
                    'owner': projects_data[2],
                    'tanggal_mulai': projects_data[3],
                    'tanggal_akhir': projects_data[4],
                    'keterangan': projects_data[5],
                    'created_at': projects_data[6],
                    'updated_at': projects_data[7]
                }
                
                container = projects_data
                code = status.HTTP_200_OK
            else:
                code = status.HTTP_204_NO_CONTENT
        else:     
            message = "Request Not Allowed"
            error.append(message)
            code = status.HTTP_405_METHOD_NOT_ALLOWED
    
    else:
        if request.method == 'GET':
            sql = "SELECT projects.id, projects.judul, users.username as owner, projects.tanggal_mulai, projects.tanggal_akhir, projects.keterangan, projects.created_at, projects.updated_at FROM projects JOIN users ON projects.owner_id = users.id"
            cursor.execute(sql)
            res = cursor.fetchall()
            close_DB()
            
            projects_data = list()
            
            for r in res:
                temp = {
                    'id': r[0],
                    'judul': r[1],
                    'owner': r[2],
                    'tanggal_mulai': r[3],
                    'tanggal_akhir': r[4],
                    'keterangan': r[5],
                    'created_at': r[6],
                    'updated_at': r[7]
                }
                
                projects_data.append(temp)
                           
            if len(projects_data) > 0:
                container = projects_data
                code = status.HTTP_200_OK
            else:
                code = status.HTTP_204_NO_CONTENT
                
        elif request.method == 'POST':
            projects_data = request.get_json()
            
            judul = projects_data['judul']
            owner_id = projects_data['owner_id']
            tanggal_mulai = projects_data['tanggal_mulai']
            tanggal_akhir = projects_data['tanggal_akhir']
            keterangan = projects_data['keterangan']
            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()
            
            sql = "INSERT INTO projects VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)"
            val = (judul, owner_id, tanggal_mulai, tanggal_akhir, keterangan, created_at, updated_at)
            
            cursor.execute(sql, val)
            conn.commit()
            close_DB()
            
            code = status.HTTP_202_ACCEPTED
            
        elif request.method == 'PUT':
            projects_data = request.get_json()
            
            project_id = projects_data['id']
            
            judul = projects_data['judul']
            tanggal_mulai = projects_data['tanggal_mulai']
            tanggal_akhir = projects_data['tanggal_akhir']
            keterangan = projects_data['keterangan']
            
            updated_at = datetime.datetime.now()
            
            sql = "UPDATE projects SET judul=%s, tanggal_mulai=%s, tanggal_akhir=%s, keterangan=%s WHERE id=%s"
            val = (judul, tanggal_mulai, tanggal_akhir, keterangan, project_id)
            
            cursor.execute(sql, val)
            conn.commit()
            close_DB()
            
            code = status.HTTP_202_ACCEPTED
            
        elif request.method == 'DELETE':
            project_data = request.get_json()
            
            project_id = project_data['id']
            
            sql = "DELETE FROM projects WHERE id=%s"
            val = (project_id)
            
            cursor.execute(sql, val)
            conn.commit()
            close_DB()
            
            code = status.HTTP_202_ACCEPTED
        
    meta = {'copyright': 'Copyright 2021 Memofy Dev'}
        
    result = {'code': code, 'data': container, 'errors': error, 'meta': meta}
    
    return jsonify(result), code

# *************************
# END OF PROJECTS THINGS
# *************************


# *************************
# BUGS THINGS
# *************************

@cross_origin()
@app.route(DEFAULT_ROOT + '/bugs', methods=['POST', 'GET', 'PUT', 'DELETE'])
@app.route(DEFAULT_ROOT + '/bug/<id>', methods=['GET'])
@app.route(DEFAULT_ROOT + '/bug/<id_dev>/developer', methods=['GET'])
def bugs(id = 0, id_dev = 0):
    open_DB()
    
    container = []
    error = []
    meta = {}
    code = ''
    
    if id != 0:
        if request.method == 'GET':
            sql = "SELECT bugs.id, bugs.judul, bugs.keterangan, projects.judul as proyek, bugs.deadline, bug_status.nama as status, severities.nama as dampak, bugs.created_at, bugs.updated_at FROM bugs JOIN projects ON bugs.projects_id = projects.id JOIN bug_status ON bugs.status_id = bug_status.id JOIN severities ON bugs.severity_id = severities.id WHERE bugs.id=%s"
            val = (id)
            cursor.execute(sql, val)
            bugs_data = cursor.fetchone()            
            close_DB()
            
            if bugs_data:
                temp = {
                    'id': bugs_data[0],
                    'judul': bugs_data[1],
                    'keterangan': bugs_data[2],
                    'proyek': bugs_data[3],
                    'deadline': bugs_data[4],
                    'status': bugs_data[5],
                    'dampak': bugs_data[6],
                    'created_at': bugs_data[7],
                    'updated_at': bugs_data[8]
                }
                
                container = temp
                code = status.HTTP_200_OK
            else:
                code = status.HTTP_204_NO_CONTENT
                
        else:     
            message = "Request Not Allowed"
            error.append(message)
            code = status.HTTP_405_METHOD_NOT_ALLOWED
    
    elif id_dev != 0:
        if request.method != 'GET':
            bugs_data = list()
            
            sql = "SELECT bugs.id, bugs.judul, bugs.keterangan, projects.judul as proyek, bugs.deadline, bug_status.nama as status, severities.nama as dampak, bugs.created_at, bugs.updated_at FROM bugs JOIN projects ON bugs.projects_id = projects.id JOIN bug_status ON bugs.status_id = bug_status.id JOIN severities ON bugs.severity_id = severities.id JOIN assignees ON bugs.id = assignees.bug_id WHERE assignees.developer_id=%s"
            val = (id_dev)
            cursor.execute(sql, val)
            res = cursor.fetchall()
            close_DB()
            
            for r in res:
                temp = {
                    'id': r[0],
                    'judul': r[1],
                    'keterangan': r[2],
                    'proyek': r[3],
                    'deadline': r[4],
                    'status': r[5],
                    'dampak': r[6],
                    'created_at': r[7],
                    'updated_at': r[8]
                }
                
                bugs_data.append(temp)
                
            if len(bugs_data) > 0:
                container = bugs_data
                code = status.HTTP_200_OK
            else:
                code = status.HTTP_204_NO_CONTENT
                
    else:
        if request.method == 'GET':
            sql = "SELECT bugs.id, bugs.judul, bugs.keterangan, projects.judul as proyek, bugs.deadline, bug_status.nama as status, severities.nama as dampak, bugs.created_at, bugs.updated_at FROM bugs JOIN projects ON bugs.projects_id = projects.id JOIN bug_status ON bugs.status_id = bug_status.id JOIN severities ON bugs.severity_id = severities.id"
            cursor.execute(sql)
            res = cursor.fetchall()
            close_DB()
            
            bugs_data = list()
            
            for r in res:
                temp = {
                    'id': r[0],
                    'judul': r[1],
                    'keterangan': r[2],
                    'proyek': r[3],
                    'deadline': r[4],
                    'status': r[5],
                    'dampak': r[6],
                    'created_at': r[7],
                    'updated_at': r[8]
                }
                
                bugs_data.append(temp)
                
            if len(bugs_data) > 0:
                container = bugs_data
                code = status.HTTP_200_OK
            else:
                code = status.HTTP_204_NO_CONTENT
                
        elif request.method == 'POST':
            bugs_data = request.get_json()
            
            developers = bugs_data['developers']
            
            judul = bugs_data['judul']
            keterangan = bugs_data['keterangan']
            projects_id = bugs_data['projects_id']
            deadline = bugs_data['deadline']
            status_id = bugs_data['status_id']
            severity_id = bugs_data['severity_id']
            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()
            
            sql = "INSERT INTO bugs VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)"
            val = (judul, keterangan, projects_id, deadline, status_id, severity_id, created_at, updated_at)
            
            cursor.execute(sql, val)
            conn.commit()
            close_DB()
            
            # developers insertion
            open_DB()
            
            last_data = get_last_id('bugs')
            
            for developer in developers:
                sql = "INSERT INTO assignees VALUES (NULL, %s, %s, %s, %s)"
                val = (last_data['id'], developer, created_at, updated_at)
                
                cursor.execute(sql, val)
                conn.commit()
            
            close_DB()
            
            code = status.HTTP_202_ACCEPTED
            
        elif request.method == 'PUT':
            bugs_data = request.get_json()
            
            bugs_id = bugs_data['id']
            
            judul = bugs_data['judul']
            keterangan = bugs_data['keterangan']
            deadline = bugs_data['deadline']
            status_id = bugs_data['status_id']
            severity_id = bugs_data['severity_id']
            
            updated_at = datetime.datetime.now()
            
            sql = "UPDATE bugs SET judul=%s, keterangan=%s, deadline=%s, status_id=%s, severity_id=%s WHERE id=%s"
            val = (judul, keterangan, deadline, status_id, severity_id, bugs_id)
            
            cursor.execute(sql, val)
            conn.commit()
            close_DB()
            
            code = status.HTTP_202_ACCEPTED
            
        elif request.method == 'DELETE':
            bugs_data = request.get_json()
            
            bugs_id = bugs_data['id']
            
            sql = "DELETE FROM bugs WHERE id=%s"
            val = (bugs_id)
            
            cursor.execute(sql, val)
            conn.commit()
            close_DB()
            
            code = status.HTTP_202_ACCEPTED
        
    meta = {'copyright': 'Copyright 2021 Memofy Dev'}
        
    result = {'code': code, 'data': container, 'errors': error, 'meta': meta}
    
    return jsonify(result), code


@cross_origin()
@app.route(DEFAULT_ROOT + '/severities', methods=['GET'])
@app.route(DEFAULT_ROOT + '/severity/<id>', methods=['GET'])
def severity(id = 0):
    open_DB()
    
    container = []
    error = []
    meta = {}
    code = ''
    
    if id == 0 and request.method == 'GET':
        severity_data = list()
        
        sql = "SELECT * FROM severities"
        cursor.execute(sql)
        
        res = cursor.fetchall()
        for r in res:
            temp = {
                'id': r[0],
                'nama': r[1],
                'created_at': r[2],
                'updated_at': r[3]
            }
            
            severity_data.append(temp)    
        
        if len(severity_data) > 0:
            container = severity_data
            code = status.HTTP_200_OK
        else:
            code = status.HTTP_204_NO_CONTENT
            
    elif request.method == 'GET':
        sql = "SELECT * FROM severities WHERE id=%s"
        val = (id)
        cursor.execute(sql, val)
        
        severity_data = cursor.fetchone()
        
        if severity_data:
            temp = {
                'id': severity_data[0],
                'nama': severity_data[1],
                'created_at': severity_data[2],
                'updated_at': severity_data[3]
            }
            
            container = temp
            code = status.HTTP_200_OK
        else:
            code = status.HTTP_204_NO_CONTENT
            
    else:
        message = "Request not allowed"
        error.append(message)
        
        code = status.HTTP_405_METHOD_NOT_ALLOWED
        
    meta = {'copyright': 'Copyright 2021 Memofy Dev'}
        
    result = {'code': code, 'data': container, 'errors': error, 'meta': meta}
    
    return jsonify(result), code


@cross_origin()
@app.route(DEFAULT_ROOT + '/status', methods=['GET'])
@app.route(DEFAULT_ROOT + '/status/<id>', methods=['GET'])
def bug_status(id = 0):
    open_DB()
    
    container = []
    error = []
    meta = {}
    code = ''
    
    if id == 0 and request.method == 'GET':
        status_data = list()
        
        sql = "SELECT * FROM bug_status"
        cursor.execute(sql)
        
        res = cursor.fetchall()
        for r in res:
            temp = {
                'id': r[0],
                'nama': r[1],
                'created_at': r[2],
                'updated_at': r[3]
            }
            
            status_data.append(temp)    
        
        if len(status_data) > 0:
            container = status_data
            code = status.HTTP_200_OK
        else:
            code = status.HTTP_204_NO_CONTENT
            
    elif request.method == 'GET':
        sql = "SELECT * FROM bug_status WHERE id=%s"
        val = (id)
        cursor.execute(sql, val)
        
        status_data = cursor.fetchone()
        
        if status_data:
            temp = {
                'id': status_data[0],
                'nama': status_data[1],
                'created_at': status_data[2],
                'updated_at': status_data[3]
            }
            
            container = temp
            code = status.HTTP_200_OK
        else:
            code = status.HTTP_204_NO_CONTENT
            
    else:
        message = "Request not allowed"
        error.append(message)
        
        code = status.HTTP_405_METHOD_NOT_ALLOWED
        
    meta = {'copyright': 'Copyright 2021 Memofy Dev'}
        
    result = {'code': code, 'data': container, 'errors': error, 'meta': meta}
    
    return jsonify(result), code

# *************************
# END OF BUGS THINGS
# *************************