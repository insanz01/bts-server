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
#                                 DATABASE
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
def users(id = 0):
    open_DB()
    
    container = []
    error = []
    meta = {}
    code = ''
    
    if id != 0:
        if request.method == 'GET':
            sql = "SELECT users.id, users.username, users.nama_pengguna, users.nomor_hp, users.email, roles.nama as role, users.created_at, users.updated_at FROM users JOIN roles ON users.role_id = roles.id WHERE users.id=%s"
            val = (id)
            cursor.execute(sql, val)
            userdata = cursor.fetchone()            
            close_DB()
            
            if userdata:
                container.append(userdata)
                code = status.HTTP_200_OK
            else:
                code = status.HTTP_204_NO_CONTENT
        else:     
            message = "Request Not Allowed"
            error.append(message)
            code = status.HTTP_405_METHOD_NOT_ALLOWED
    
    else:
        if request.method == 'GET':
            sql = "SELECT users.id, users.username, users.nama_pengguna, users.nomor_hp, users.email, roles.nama as role, users.created_at, users.updated_at FROM users JOIN roles ON users.role_id = roles.id"
            cursor.execute(sql)
            res = cursor.fetchall()
            close_DB()
            
            userdata = list()
            
            for r in res:
                userdata.append(r)
                
            container.append(userdata)
            if len(container) > 0:
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
            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()
            
            sql = "INSERT INTO users VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (username, password, nama_pengguna, nomor_hp, email, role_id, created_at, updated_at)
            
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
            
            updated_at = datetime.datetime.now()
            
            sql = "UPDATE users SET username=%s, nama_pengguna=%s, nomor_hp=%s, email=%s, role_id=%s WHERE id=%s"
            val = (username, nama_pengguna, nomor_hp, email, role_id, user_id)
            
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
                    roles_data.append(r)
                    
                container.append(roles_data)
                
                if len(container) > 0:
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
                    container.append(roles_data)
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
                container.append(projects_data)
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
                projects_data.append(r)
                
            container.append(projects_data)
            
            if len(container) > 0:
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
def bugs(id = 0):
    open_DB()
    
    container = []
    error = []
    meta = {}
    code = ''
    
    if id != 0:
        if request.method == 'GET':
            sql = "SELECT bugs.id, bugs.judul, bugs.keterangan, projects.judul as proyek, bugs.deadline, bug_status.nama as status, severities.nama as dampak, bugs.created_at, bugs.updated_at FROM bugs JOIN projects ON bugs.projects_id = projects.id JOIN bug_status ON bugs.status_id = bug_status.id JOIN severities ON bugs.severity_id ON severities.id WHERE bugs.id=%s"
            val = (id)
            cursor.execute(sql, val)
            bugs_data = cursor.fetchone()            
            close_DB()
            
            if bugs_data:
                container.append(bugs_data)
                code = status.HTTP_200_OK
            else:
                code = status.HTTP_204_NO_CONTENT
        else:     
            message = "Request Not Allowed"
            error.append(message)
            code = status.HTTP_405_METHOD_NOT_ALLOWED
    
    else:
        if request.method == 'GET':
            sql = "SELECT bugs.id, bugs.judul, bugs.keterangan, projects.judul as proyek, bugs.deadline, bug_status.nama as status, severities.nama as dampak, bugs.created_at, bugs.updated_at FROM bugs JOIN projects ON bugs.projects_id = projects.id JOIN bug_status ON bugs.status_id = bug_status.id JOIN severities ON bugs.severity_id ON severities.id WHERE bugs.id=%s"
            cursor.execute(sql)
            res = cursor.fetchall()
            close_DB()
            
            bugs_data = list()
            
            for r in res:
                bugs_data.append(r)
                
            container.append(bugs_data)
            
            if len(container) > 0:
                code = status.HTTP_200_OK
            else:
                code = status.HTTP_204_NO_CONTENT
                
        elif request.method == 'POST':
            bugs_data = request.get_json()
            
            judul = bugs_data['judul']
            keterangan = bugs_data['keterangan']
            projects_id = bugs_data['projects_id']
            deadline = bugs_data['deadline']
            status_id = bugs_data['status_id']
            severity_id = bugs_data['severity_id']
            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()
            
            sql = "INSERT INTO projects VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)"
            val = (judul, keterangan, projects_id, deadline, status_id, severity_id, created_at, updated_at)
            
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

# *************************
# END OF BUGS THINGS
# *************************