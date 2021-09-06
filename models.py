from os import curdir
import re
from . import mysql
from flask import Blueprint, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import base64
import io
from PIL import Image

model = Blueprint('model', __name__)

totalColiformStatus = ['Absent', 'Present', 'Not Tested', 'Result Awaiting']


def get_reading_value_status_by_element(element, value):
    reading_value = value
    if value == -99:
        reading_value = 'N/A'
    elif value == -999:
        reading_value = 'Not Tested'
    elif element == 'TOTALCOLIFORM' and value >= 0 and value <= 3:
        reading_value = totalColiformStatus[int(value)]

    return reading_value


def get_limit_range_by_element(elements: dict, name: str) -> str:
    rangeString = ''
    if name == 'TOTALCOLIFORM' or name == 'ORP':
        rangeString = '-'

    elif elements[name]['min'] == 0:
        rangeString = str(elements[name]['max'])
        # '<= ' +

    elif elements[name]['max'] == 0:
        rangeString = '>= ' + str(elements[name]['min'])
        #  \u2265
        print(rangeString)

    else:
        rangeString = str(elements[name]['min']) + \
            ' to ' + str(elements[name]['max'])

    if elements[name]['standard'] == 1:
        rangeString += '*'

    elif elements[name]['standard'] == 2:
        rangeString += '**'

    elif elements[name]['standard'] == 3:
        rangeString += '***'

    elif elements[name]['standard'] == 4:
        rangeString += '****'

    return rangeString


def get_category_from_station_type(stationType: str) -> str:
    if stationType in {
        'River',
        'Water Body',
        'Piezometer'
    }:
        return stationType

    elif stationType in {
        'Dam',
        'Irrigation Scheme',
        'Lake'
    }:
        return 'Water Body'

    elif stationType in {
        'Tube Well',
        'Dug Well'
    }:
        return 'Piezometer'

    else:
        return stationType


class User:
    def __init__(self, id, name, password, email, admin):
        self.id = id
        self.name = name
        self.password = password
        self.email = email
        self.admin = admin

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.name

    def get_password(self):
        return self.password

    def is_admin(self):
        return self.admin >= 1

    def is_root(self):
        return self.admin == 2

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)

    @staticmethod
    def create_user(username, password, email, admin):
        cursor = mysql.connection.cursor()

        cursor.execute("INSERT INTO user( \
                            name, \
                            password, \
                            email, \
                            admin) \
                            VALUES \
                            (%s, %s, %s, %s);", (username, generate_password_hash(password), email, admin))
        mysql.connection.commit()
        cursor.close()

        return {'msg': 'User added.'}

    @staticmethod
    def get_user(userName):
        cursor = mysql.connection.cursor()

        getUserQuery = "select * from user where name = %s limit 1;"
        # print(getUserQuery)
        cursor.execute(getUserQuery, (userName,))

        result = cursor.fetchall()

        user = None

        if len(result) > 0:
            # print(result[0][1])
            user = User(id=result[0][0], name=result[0][1],
                        password=result[0][2], email=result[0][3],
                        admin=result[0][4])

        # print(result)
        cursor.close()
        return user

    @staticmethod
    def get_user_by_id(id):
        cursor = mysql.connection.cursor()

        getUserQuery = "select * from user where id = %s;"
        # print(getUserQuery)
        cursor.execute(getUserQuery, (id,))

        result = cursor.fetchall()

        user = None

        if len(result) > 0:
            # print(result[0][1])
            user = {'id': result[0][0], 'name': result[0][1],
                    'email': result[0][3], 'admin': result[0][4]}

        # print(result)
        cursor.close()
        return user

    @staticmethod
    def get_user_by_name_not_id(name, id):
        cursor = mysql.connection.cursor()

        getUserQuery = "select * from user where name=%s and id<>%s;"
        cursor.execute(getUserQuery, (name, id,))

        result = cursor.fetchall()

        user = None

        if len(result) > 0:
            # print(result[0][1])
            user = {'id': result[0][0], 'name': result[0][1],
                    'email': result[0][3], 'admin': result[0][4]}

        cursor.close()
        return user

    @staticmethod
    def update_user(id, name, email, admin):
        cursor = mysql.connection.cursor()

        updateUserQuery = "UPDATE user SET name = %s, \
                email = %s, admin = %s WHERE id = %s;"

        # print(updateUserQuery)
        cursor.execute(updateUserQuery, (name, email, admin, id))

        mysql.connection.commit()

        msg = 'User updated.'

        cursor.close()
        return {'msg': msg}

    @staticmethod
    def update_password(id, password):
        cursor = mysql.connection.cursor()

        updateUserQuery = "UPDATE user SET password = %s WHERE id = %s;"

        # print(updateUserQuery)
        cursor.execute(updateUserQuery, (generate_password_hash(password), id))

        mysql.connection.commit()

        msg = 'Password updated'

        cursor.close()
        return {'msg': msg}

    @staticmethod
    def delete_user(id):
        cursor = mysql.connection.cursor()

        deleteUserQuery = "DELETE from user where id=%s;"
        # print(deleteUserQuery)
        cursor.execute(deleteUserQuery, (id,))

        mysql.connection.commit()
        cursor.close()

        msg = 'User deleted.'

        return {'msg': msg}

    @staticmethod
    def get_users():
        cursor = mysql.connection.cursor()

        getUsersQuery = "select * from user;"
        # print(getUsersQuery)
        cursor.execute(getUsersQuery)

        results = cursor.fetchall()

        users = None

        if len(results) > 0:
            # print(result[0][1])
            users = [{'id': result[0], 'name': result[1],
                      'email':result[3], 'admin': result[4]} for result in results]

        # print(users)
        cursor.close()
        return users

    @staticmethod
    def get_admin_count():
        cursor = mysql.connection.cursor()

        getAdminCountQuery = "SELECT count(*) FROM user where admin = 1;"
        # print(getAdminCountQuery)
        cursor.execute(getAdminCountQuery)

        result = cursor.fetchall()

        adminCount = 0

        if len(result) > 0:
            # print(result[0][1])
            adminCount = int(result[0][0])

        # print(result)
        cursor.close()
        return adminCount


class Element:
    def __init__(self, id, name, unit, min, max):
        self.id = id
        self.name = name
        self.unit = unit
        self.min = min
        self.max = max

    @staticmethod
    def get_elements():
        cursor = mysql.connection.cursor()

        getElementsQuery = "select * from element_master;"
        # print(getElementsQuery)
        cursor.execute(getElementsQuery)

        results = cursor.fetchall()

        elements = None

        if len(results) > 0:
            # print(result[0][1])
            elements = [{'id': result[0], 'name': result[1], 'unit':result[2],
                         'min': result[3], 'max': result[4]} for result in results]

        # print(elements)
        cursor.close()
        return elements

    @staticmethod
    def get_elements_dict():
        cursor = mysql.connection.cursor()

        getElementsQuery = "select * from element_master;"
        # print(getElementsQuery)
        cursor.execute(getElementsQuery)

        results = cursor.fetchall()

        elements = {}

        if len(results) > 0:
            # print(result[0][1])
            for result in results:
                elements[result[1]] = {'min': result[3],
                                       'max': result[4],
                                       'unit': result[2],
                                       'standard': result[5]}

        # print(elements)
        cursor.close()
        return elements

    @staticmethod
    def get_element_readings_dict(group_id):
        cursor = mysql.connection.cursor()

        getReadingsQuery = "SELECT element_name, reading_value FROM element_reading where group_id = %s"
        cursor.execute(getReadingsQuery, (group_id, ))

        results = cursor.fetchall()

        readings = {}

        if len(results) > 0:
            for result in results:
                readings[result[0]] = result[1]

        cursor.close()
        return readings

    @staticmethod
    def get_element_readings_array(group_id: str) -> list:
        cursor = mysql.connection.cursor()

        getReadingsQuery = "SELECT element_name, reading_value, valid FROM element_reading where group_id = %s order by id;"

        cursor.execute(getReadingsQuery, (group_id, ))

        results = cursor.fetchall()
        cursor.close()

        return results

    @staticmethod
    def get_element_names():
        cursor = mysql.connection.cursor()

        getElementsQuery = "select name from element_master;"
        # print(getElementsQuery)
        cursor.execute(getElementsQuery)

        results = cursor.fetchall()

        elements = None

        if len(results) > 0:
            # print(result[0][1])
            elements = [[result[0]] for result in results]

        # print(elements)
        cursor.close()
        return elements

    @staticmethod
    def get_element(id):
        cursor = mysql.connection.cursor()

        getElementsQuery = "select * from element_master where id='" + id + "';"
        cursor.execute(getElementsQuery)

        results = cursor.fetchall()

        element = None

        if len(results) > 0:
            # print(result[0][1])
            element = {'id': results[0][0], 'name': results[0][1], 'unit': results[0][2],
                       'min': results[0][3], 'max': results[0][4]}

        cursor.close()
        return element

    @staticmethod
    def get_element_by_name(name):
        cursor = mysql.connection.cursor()

        getElementsQuery = "select * from element_master where name='" + name + "';"
        cursor.execute(getElementsQuery)

        results = cursor.fetchall()

        element = None

        if len(results) > 0:
            # print(result[0][1])
            element = {'id': results[0][0], 'name': results[0][1],
                       'unit': results[0][2]}

        cursor.close()
        return element

    @staticmethod
    def get_element_by_name_not_id(name, id):
        cursor = mysql.connection.cursor()

        getElementsQuery = "select * from element_master where name='" + \
            name + "' and id<>'" + id + "';"
        cursor.execute(getElementsQuery)

        results = cursor.fetchall()

        element = None

        if len(results) > 0:
            # print(result[0][1])
            element = {'id': results[0][0], 'name': results[0][1],
                       'unit': results[0][2]}

        cursor.close()
        return element

    @staticmethod
    def update_element(element):
        cursor = mysql.connection.cursor()

        getElementsQuery = "select name from element_master where id='" + element.id + "';"
        cursor.execute(getElementsQuery)
        results = cursor.fetchall()
        currentName = results[0][0]

        if currentName != element.name:
            updateElementNameInReadings = "UPDATE element_reading SET element_name = %s \
                WHERE element_name = %s"
            cursor.execute(updateElementNameInReadings,
                           (element.name, currentName, ))

        updateElementsQuery = "UPDATE element_master SET name = '" + element.name + \
            "', unit = '" + element.unit + "', min = '" + element.min + "', max = '" + \
            element.max + "' where id='" + element.id + "';"
        # print(updateElementsQuery)
        cursor.execute(updateElementsQuery)

        mysql.connection.commit()

        msg = 'Record updated.'

        cursor.close()
        return {'msg': msg}

    @staticmethod
    def create_element(name, unit, min, max):
        cursor = mysql.connection.cursor()

        cursor.execute("INSERT INTO element_master( \
                            name, \
                            unit, \
                            min, \
                            max) \
                            VALUES \
                            (%s, %s, %s, %s);", (name, unit, min, max))
        mysql.connection.commit()
        cursor.close()

        return {'msg': 'Record added.'}

    @staticmethod
    def delete_element(id):
        cursor = mysql.connection.cursor()

        deleteElementsQuery = "DELETE from element_master where id='" + id + "';"
        # print(deleteElementsQuery)
        cursor.execute(deleteElementsQuery)

        mysql.connection.commit()
        cursor.close()

        msg = 'Record deleted.'

        return {'msg': msg}

    @staticmethod
    def get_reading(start, end):
        cursor = mysql.connection.cursor()

        getElementReadingQuery = "SELECT date_format(reading_time, '%Y-%m-%d %H:%i:%s'), reading_value FROM element_reading where \
            reading_time >= '" + start + "' and reading_time < '" + end + "' order by reading_time;"
        # print(getElementReadingQuery)
        cursor.execute(getElementReadingQuery)

        results = cursor.fetchall()

        data = []
        labels = []

        if len(results) > 0:
            for result in results:
                if result[1] == -99:
                    continue
                data.append([result[0], result[1]])

        cursor.close()
        return {'data': data}

    @staticmethod
    def get_reading_records(search, start, end):
        cursor = mysql.connection.cursor()

        searchClause = ""
        startClause = ""
        endClause = ""

        if len(search) > 0:
            searchClause = "and (element_name like '" + search + "%' \
                            or reading_value like '" + search + "%' \
                            or location like '" + search + "%') "

        if len(start) > 0:
            startClause = "and reading_time >= '" + start + "' "

        if len(end) > 0:
            endClause = "and reading_time < '" + end + "' "

        getElementReadingQuery = "SELECT er.id, element_name, reading_value, unit, \
                date_format(reading_time, '%Y-%m-%d'), date_format(reading_time, '%h:%i:%s %p'), \
                location, lat, lng FROM element_reading er, element_master where name = element_name \
                " + searchClause + startClause + endClause + " order by id;"

        # print(getElementReadingQuery)
        cursor.execute(getElementReadingQuery)

        results = cursor.fetchall()

        records = []

        count = len(results)

        if count > 0:
            for result in results:
                records.append({"id": result[0], "element_name": result[1], "reading_value": get_reading_value_status_by_element(result[1], result[2]),
                                "unit": result[3], "date": result[4], "time": result[5], "location": result[6],
                                "latitude": float(result[7]), "longitude": float(result[8])})

        cursor.close()
        return {"elements": records}

    @staticmethod
    def get_reading_records(search, start, end, offset, limit):
        cursor = mysql.connection.cursor()

        searchClause = ""
        startClause = ""
        endClause = ""

        if len(search) > 0:
            searchClause = "and (element_name like '" + search + "' \
                            or reading_value like '" + search + "%' \
                            or location like '" + search + "' \
                            or station_id like '" + search + "%'\
                            or waterbody_name like '" + search + "') "

        if len(start) > 0:
            startClause = "and reading_time >= '" + start + "' "

        if len(end) > 0:
            endClause = "and reading_time < '" + end + "' "

        getElementReadingCountQuery = "SELECT count(er.id) FROM element_reading er, \
                element_master where name = element_name \
                " + searchClause + startClause + endClause + " ;"

        totalCount = 0
        cursor.execute(getElementReadingCountQuery)
        results = cursor.fetchall()

        if len(results) > 0:
            totalCount = results[0][0]

        getElementReadingQuery = "SELECT er.id, element_name, reading_value, unit, \
                date_format(reading_time, '%Y-%m-%d'), date_format(reading_time, '%h:%i:%s %p'), \
                location, lat, lng, valid, station_id, waterbody_name FROM element_reading er, \
                element_master where name = element_name " + searchClause + startClause + \
            endClause + " order by id desc limit " + \
            str(limit) + " offset " + str(offset) + ";"

        # print(getElementReadingQuery)
        cursor.execute(getElementReadingQuery)

        results = cursor.fetchall()

        records = []

        count = len(results)

        if count > 0:
            for result in results:
                records.append({"id": result[0], "element_name": result[1], "reading_value": get_reading_value_status_by_element(result[1], result[2]),
                                "unit": result[3], "date": result[4], "time": result[5], "location": result[6],
                                "latitude": float(result[7]), "longitude": float(result[8]), "valid": result[9],
                                "station_id": result[10], "water_body": result[11]})

        cursor.close()
        return {"elements": records, "totalCount": totalCount, "count": count}

    @staticmethod
    def get_reading_records_location(search, location, start, end, offset, limit):
        cursor = mysql.connection.cursor()

        searchClause = ""
        startClause = ""
        endClause = ""

        if len(search) > 0:
            searchClause = "and (element_name like '" + search + "' \
                            or reading_value like '" + search + "%' \
                            or waterbody_name like '" + search + "') "

        if len(start) > 0:
            startClause = "and reading_time >= '" + start + "' "

        if len(end) > 0:
            endClause = "and reading_time < '" + end + "' "

        getElementReadingCountQuery = "SELECT count(er.id) FROM element_reading er, \
                element_master where name = element_name and location = '" + location + "' \
                " + searchClause + startClause + endClause + " ;"

        totalCount = 0
        cursor.execute(getElementReadingCountQuery)
        results = cursor.fetchall()

        if len(results) > 0:
            totalCount = results[0][0]

        getElementReadingQuery = "SELECT er.id, element_name, reading_value, unit, \
                date_format(reading_time, '%Y-%m-%d'), date_format(reading_time, '%h:%i:%s %p'), \
                location, lat, lng, valid, waterbody_name FROM element_reading er, element_master \
                where name = element_name and location = '" + location + "' " + searchClause + \
            startClause + endClause + " order by id desc limit " + \
            str(limit) + " offset " + str(offset) + ";"

        # print(getElementReadingQuery)
        cursor.execute(getElementReadingQuery)

        results = cursor.fetchall()

        records = []

        count = len(results)

        if count > 0:
            for result in results:
                records.append({"id": result[0], "element_name": result[1], "reading_value": get_reading_value_status_by_element(result[1], result[2]),
                                "unit": result[3], "date": result[4], "time": result[5], "location": result[6],
                                "latitude": float(result[7]), "longitude": float(result[8]), "valid": result[9],
                                "water_body": result[10]})

        cursor.close()
        return {"elements": records, "totalCount": totalCount, "count": count}

    @staticmethod
    def get_reading_records_csv(search, start, end):
        cursor = mysql.connection.cursor()

        searchClause = ""
        startClause = ""
        endClause = ""

        if len(search) > 0:
            searchClause = "and (element_name like '" + search + "' \
                            or reading_value like '" + search + "%' \
                            or location like '" + search + "' \
                            or station_id like '" + search + "%'\
                            or waterbody_name like '" + search + "') "

        if len(start) > 0:
            startClause = "and reading_time >= '" + start + "' "

        if len(end) > 0:
            endClause = "and reading_time < '" + end + "' "

        getElementReadingQuery = "SELECT er.id, element_name, reading_value, unit, \
                date_format(reading_time, '%Y-%m-%d'), date_format(reading_time, '%h:%i:%s %p'), \
                location, lat, lng, station_id, waterbody_name FROM element_reading er, \
                element_master where name = element_name " + searchClause + startClause + endClause + " order by id;"

        # print(getElementReadingQuery)
        cursor.execute(getElementReadingQuery)

        results = cursor.fetchall()

        records = [["Id", "Element Name", "Reading Value", "Unit",
                    "Date", "Time", "Location", "Latitude", "Longitude", "Station", "Water Body"]]

        total = len(results)

        if total > 0:
            for result in results:
                records.append([result[0], result[1], get_reading_value_status_by_element(result[1], result[2]), result[3], result[4], result[5],
                                result[6], float(result[7]), float(result[8]), result[9], result[10]])

        cursor.close()
        return records

    @staticmethod
    def get_reading_trends(start, end, location, station, elementName):
        cursor = mysql.connection.cursor()

        getElementReadingQuery = "SELECT date_format(reading_time, '%Y-%m-%d %H:%i:%s'), reading_value FROM element_reading where \
            reading_time >= '" + start + "' and reading_time < '" + end + "' \
            and location = '" + location + "' and station_id = '" + station + "' \
            and element_name = '" + elementName + "' order by reading_time;"

        # print(getElementReadingQuery)
        cursor.execute(getElementReadingQuery)

        results = cursor.fetchall()

        data = []
        labels = []

        if len(results) > 0:
            for result in results:
                if result[1] == -99 or result[1] == -999:
                    continue
                data.append([result[0], result[1]])

        cursor.close()
        return {'data': data, 'unit': Element.get_element_by_name(elementName)['unit']}

    @staticmethod
    def get_reading_records_report(location, station, date):
        cursor = mysql.connection.cursor()

        getElementReadingQuery = "SELECT er.id, element_name, reading_value, unit, \
            date_format(reading_time, '%h:%i:%s %p'), waterbody_name, \
            lat, lng, er.group_id FROM element_reading er, element_master where \
            name = element_name and date(reading_time) = '" + date + "' \
            and location = '" + location + "' and station_id = '" + station + "' \
            order by id;"

        # print(getElementReadingQuery)
        cursor.execute(getElementReadingQuery)

        results = cursor.fetchall()

        data = []
        labels = []
        i = 1
        records = []
        water_body = ''
        group_id = ''
        reading_time = ''

        if len(results) > 0:
            for result in results:
                records.append({"id": i, "element_name": result[1], "reading_value": get_reading_value_status_by_element(result[1], result[2]),
                                "unit": result[3], "time": result[4], "latitude": float(result[6]),
                                "longitude": float(result[7])})
                i += 1
            water_body = results[0][5]
            group_id = str(results[len(results) - 1][8])
            reading_time = results[len(results) - 1][4]

        getImageQuery = "SELECT file_name, image FROM reading_images where reading_group_id = '" + group_id + "'"

        cursor.execute(getImageQuery)

        results = cursor.fetchall()
        binaryImage = ''
        image = ''
        fileName = ''
        imHeight = 0
        imWidth = 0

        if len(results) > 0:
            fileName = results[0][0]
            binaryImage = results[0][1]
            img = Image.open(io.BytesIO(binaryImage))
            imWidth, imHeight = img.size
            # print("Width: " + str(imWidth) + ", Height: " + str(imHeight))
            img.close()

        finalImange = image
        if len(binaryImage) > 0:
            finalImange = base64.b64encode(binaryImage).decode('utf-8')

        cursor.close()
        return {"elements": records, "water_body": water_body, "reading_time": reading_time, "image_file_name": fileName,
                "image": finalImange, "imageWidth": imWidth, "imageHeight": imHeight}

    @staticmethod
    def get_locations_readings():
        cursor = mysql.connection.cursor()

        getLocationsQuery = "SELECT distinct location FROM element_reading where location <> '';"

        cursor.execute(getLocationsQuery)

        results = cursor.fetchall()

        records = []
        total = len(results)

        if total > 0:
            records = [result[0] for result in results]

        cursor.close()
        return records

    @staticmethod
    def get_stations_readings() -> list:
        cursor = mysql.connection.cursor()

        getStationsQuery = "select waterbody_name, station_id, ANY_VALUE(lat), ANY_VALUE(lng) \
                            from evak_db.element_reading group by station_id, waterbody_name \
                            order by waterbody_name;"

        cursor.execute(getStationsQuery)

        results = cursor.fetchall()

        records = []
        total = len(results)

        for result in results:
            records.append(
                {
                    'waterbodyName': result[0],
                    'stationId': result[1],
                    'lat': str(result[2]),
                    'lng': str(result[3])
                }
            )

        cursor.close()
        return records

    @staticmethod
    def get_stations_readings_by_location(location):
        cursor = mysql.connection.cursor()

        getStationsQuery = "SELECT distinct station_id, waterbody_name FROM element_reading where location = '" + \
            location + "' and station_id <> ''  order by station_id;"

        cursor.execute(getStationsQuery)

        results = cursor.fetchall()

        records = []
        stationNames = []
        total = len(results)

        if total > 0:
            for result in results:
                records.append(result[0])
                stationNames.append([result[0], result[1]])

        cursor.close()
        return {'stations': records, 'stationNames': stationNames}

    @staticmethod
    def get_location_coordinates(location):
        cursor = mysql.connection.cursor()

        getCoordinatesQuery = "SELECT lat, lng FROM locations where location = '" + location + "';"

        cursor.execute(getCoordinatesQuery)

        results = cursor.fetchall()
        total = len(results)

        record = {'total': 0}

        if total > 0:
            record = {'lat': float(results[0][0]), 'lng': float(
                results[0][1]), 'total': 1}

        cursor.close()
        return record

    @staticmethod
    def set_location_coordinates(location, lat, lng):
        cursor = mysql.connection.cursor()

        cursor.execute("INSERT INTO locations \
                                (location, \
                                lat, \
                                lng) \
                                VALUES \
                                (%s, %s, %s);", (location, lat, lng))

        mysql.connection.commit()
        cursor.close()

        return {'msg': 'Record added.'}

    @staticmethod
    def get_readings_by_date_range(start: str, end: str) -> dict:
        cursor = mysql.connection.cursor()

        getGroupRecordsQuery = "select group_id, any_value(date_format(reading_time, '%%Y-%%m-%%d %%H:%%i:%%s')), \
                                any_value(location), any_value(lat), any_value(lng), any_value(station_id), \
                                any_value(waterbody_name), any_value(date_format(created_time, '%%Y-%%m-%%d %%H:%%i:%%s')) \
                                from element_reading where date(reading_time) >= %s and \
                                date(reading_time) <= %s group by group_id order by group_id;"

        # print(getGroupRecordsQuery)

        cursor.execute(getGroupRecordsQuery, (start, end, ))

        resultGroupRecords = cursor.fetchall()
        recordLength = len(resultGroupRecords)
        dictElements = Element.get_elements_dict()
        data = []

        for groupRecord in resultGroupRecords:
            dataObject = {}
            groupId = groupRecord[0]
            dataObject['group_id'] = int(groupId)
            dataObject['reading_time'] = groupRecord[1]
            dataObject['publish_time'] = groupRecord[7]
            dataObject['location'] = groupRecord[2]
            dataObject['latitude'] = str(groupRecord[3])
            dataObject['longitude'] = str(groupRecord[4])
            dataObject['station_id'] = groupRecord[5]
            dataObject['waterbody_name'] = groupRecord[6]

            imageData = Element.get_image_by_group_id(groupId)
            dataObject['image_data'] = imageData['image']
            dataObject['image_file_name'] = imageData['image_file_name']
            dataObject['image_width'] = imageData['imageWidth']
            dataObject['image_height'] = imageData['imageHeight']

            elementReadings = []

            listElementReadings = Element.get_element_readings_array(
                str(groupId))

            for elementReading in listElementReadings:
                elementObject = {}
                elementObject['element_name'] = elementReading[0]
                elementObject['reading_value'] = get_reading_value_status_by_element(
                    elementReading[0], elementReading[1])
                elementObject['unit'] = dictElements[elementReading[0]]['unit']

                elementReadings.append(elementObject)

            dataObject['element_readings'] = elementReadings

            data.append(dataObject)

        return {'data': data, 'count': recordLength}

    @staticmethod
    def get_image_by_group_id(groupId: str) -> dict:
        cursor = mysql.connection.cursor()

        getImageQuery = "SELECT file_name, image FROM reading_images where reading_group_id = %s"

        cursor.execute(getImageQuery, (groupId, ))

        results = cursor.fetchall()
        binaryImage = ''
        image = ''
        fileName = ''
        imHeight = 0
        imWidth = 0

        if len(results) > 0:
            fileName = results[0][0]
            binaryImage = results[0][1]
            img = Image.open(io.BytesIO(binaryImage))
            imWidth, imHeight = img.size
            # print("Width: " + str(imWidth) + ", Height: " + str(imHeight))
            img.close()

        finalImange = image
        if len(binaryImage) > 0:
            finalImange = base64.b64encode(binaryImage).decode('utf-8')

        cursor.close()
        return {"image_file_name": fileName, "image": finalImange, "imageWidth": imWidth, "imageHeight": imHeight}

    @staticmethod
    def get_readings_by_station(station: str) -> dict:
        cursor = mysql.connection.cursor()

        getGroupRecordsQuery = "select group_id, any_value(date_format(reading_time, '%%d-%%m-%%y')), \
                                any_value(date_format(reading_time, '%%h:%%i:%%s %%p')), \
                                any_value(date_format(created_time, '%%d-%%m-%%y')), \
                                any_value(date_format(created_time, '%%h:%%i:%%s %%p')), any_value(location), \
                                any_value(er.lat), any_value(er.lng), any_value(station_id), \
                                any_value(er.waterbody_name), any_value(district), any_value(taluka), \
                                any_value(date_format(reading_time, '%%M %%Y')), min(created_time), \
                                any_value(van_number), any_value(category) from \
                                element_reading er, site_master sm \
                                where station_id = %s and station_id = unique_id \
                                group by group_id order by group_id;"

        cursor.execute(getGroupRecordsQuery, (station, ))

        resultGroupRecords = cursor.fetchall()
        dictElements = Element.get_elements_dict()
        data = {}
        data['groups'] = []

        for groupRecord in resultGroupRecords:
            group = {}
            groupId = groupRecord[0]
            group['groupId'] = groupId
            group['monthYear'] = groupRecord[12]
            group['location'] = groupRecord[5]
            group['waterbodyName'] = groupRecord[9]
            group['stationId'] = station
            group['latitude'] = str(groupRecord[6])
            group['longitude'] = str(groupRecord[7])
            group['district'] = groupRecord[10]
            group['taluka'] = groupRecord[11]
            group['vanNumber'] = groupRecord[14]
            group['category'] = groupRecord[15]

            group['samplingDate'] = groupRecord[1]
            group['samplingTime'] = groupRecord[2]
            group['publishDate'] = groupRecord[3]
            group['publishTime'] = groupRecord[4]

            imageData = Element.get_image_by_group_id(groupId)
            group['image'] = imageData['image']
            group['imageWidth'] = imageData['imageWidth']
            group['imageHeight'] = imageData['imageHeight']

            group['element_readings'] = []

            listElementReadings = Element.get_element_readings_array(
                str(groupId))
            id = 1

            for elementReading in listElementReadings:
                elementObject = {}

                elementObject['id'] = id
                elementObject['elementName'] = elementReading[0]
                elementObject['limit'] = get_limit_range_by_element(
                    dictElements, elementReading[0])
                elementObject['readingValue'] = get_reading_value_status_by_element(
                    elementReading[0], elementReading[1])
                elementObject['unit'] = dictElements[elementReading[0]]['unit']
                elementObject['valid'] = elementReading[2]

                id += 1

                group['element_readings'].append(elementObject)

            data['groups'].append(group)

        cursor.close()
        return data

    @staticmethod
    def get_reading_groups(search: str = '', offset: int = 0, limit: int = 10) -> dict:
        cursor = mysql.connection.cursor()

        searchClause = ''

        if len(search) > 0:
            searchClause = 'and (group_id like %s \
                            or station_id like %s \
                            or waterbody_name like %s \
                            or van_number like %s) '

        getReadingGroupsCountQuery = 'select count(distinct group_id) from element_reading \
                                        where 1 = 1 ' + searchClause

        if len(searchClause):
            cursor.execute(getReadingGroupsCountQuery,
                           (search + '%%', search + '%%', search + '%%', search + '%%', ))
        else:
            cursor.execute(getReadingGroupsCountQuery)

        totalCount = 0
        results = cursor.fetchall()

        if len(results):
            totalCount = results[0][0]

        getReadingGroupsQuery = "select group_id, date_format(min(created_time), '%%Y-%%m-%%d %%h:%%i:%%s %%p'), \
                                any_value(station_id), \
                                any_value(waterbody_name), any_value(van_number) \
                                from evak_db.element_reading where 1 = 1 \
                                " + searchClause + " group by group_id \
                                order by group_id desc limit " + str(limit) + " \
                                offset " + str(offset)

        if len(searchClause):
            cursor.execute(getReadingGroupsQuery, (search + '%%',
                                                   search + '%%', search + '%%', search + '%%',))
        else:
            cursor.execute(getReadingGroupsQuery, ())
        results = cursor.fetchall()
        records = []

        for result in results:
            records.append({
                'id': result[0],
                'time': result[1],
                'station_id': result[2],
                'waterbody_name': result[3],
                'van_number': result[4]
            })

        return {'groups': records, 'count': len(results), 'totalCount': totalCount}

    @staticmethod
    def update_group_readings(groupId: str, readings: list, userName: str) -> dict:
        cur = mysql.connection.cursor()
        try:
            dictElements = Element.get_elements_dict()
            dictReadings = Element.get_element_readings_dict(groupId)
            rowCount = 0

            for reading in readings:
                element_name = reading['element_name']
                reading_value = reading['reading_value']
                valid = 2

                if element_name not in dictElements \
                        or float(dictReadings[element_name]) == float(reading_value):
                    continue

                if element_name == 'TOTALCOLIFORM':
                    if float(reading_value) == 1:
                        valid = 0

                elif (float(reading_value) != -99) \
                        and (float(reading_value) != -999) \
                        and element_name != 'ORP' \
                        and float(dictElements[element_name]['max']) == 0:
                    if float(reading_value) < float(dictElements[element_name]['min']):
                        if float(reading_value) >= (float(dictElements[element_name]['min']) * 0.75):
                            valid = 1
                        else:
                            valid = 0

                elif (float(reading_value) != -99) \
                        and (float(reading_value) != -999) \
                        and element_name != 'ORP' \
                        and (float(reading_value) < float(dictElements[element_name]['min']) or
                             float(reading_value) > float(dictElements[element_name]['max'])):
                    if float(reading_value) >= (float(dictElements[element_name]['min']) * 0.75) and \
                            float(reading_value) <= (float(dictElements[element_name]['max']) * 1.25):
                        valid = 1
                    else:
                        valid = 0

                cur.execute("UPDATE element_reading \
                            SET reading_value = %s, \
                            valid = %s, \
                            modified_time = now(), \
                            modified_by = %s \
                            WHERE group_id= % s and element_name = % s",
                            (reading_value, str(valid), userName, groupId, element_name, ))

                rowCount += 1

            mysql.connection.commit()
            cur.close()

            return jsonify({'msg': 'Success!', 'rows_updated': rowCount, 'group_id': groupId}), 200
        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            print(str(type(e).__name__) + ': ' + str(e))
            return jsonify({
                'msg': 'An error has occurred while processing the request.',
                'errorType': str(type(e).__name__),
                'error': str(e)}), 400

    @ staticmethod
    def delete_group_readings(groupId: str) -> dict:
        cur = mysql.connection.cursor()
        try:
            rowCount = 0
            deleteImageQuery = "DELETE FROM reading_images WHERE reading_group_id = %s"
            cur.execute(deleteImageQuery, (groupId, ))

            deleteReadingsQuery = "DELETE FROM element_reading WHERE group_id = %s"
            cur.execute(deleteReadingsQuery, (groupId, ))

            mysql.connection.commit()
            rowCount = cur.rowcount
            cur.close()

            return jsonify({'msg': 'Success!', 'rows_deleted': rowCount, 'group_id': groupId}), 200
        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            print(str(type(e).__name__) + ': ' + str(e))
            return jsonify({
                'msg': 'An error has occurred while processing the request.',
                'errorType': str(type(e).__name__),
                'error': str(e)}), 400

    @ staticmethod
    def update_validation_of_element_readings(elementId: str) -> dict:
        cur = mysql.connection.cursor()
        try:
            element = Element.get_element(elementId)

            if element is None:
                return jsonify({
                    'error': 'No element present with id# ' + elementId
                })

            getReadingsQuery = "select id, reading_value, valid from element_reading \
                where element_name = %s order by id"

            cur.execute(getReadingsQuery, (element['name'], ))

            results = cur.fetchall()
            updateCount = 0

            for reading in results:
                id = reading[0]
                value = reading[1]
                valid = reading[2]
                newValid = 2

                if element['name'] == 'TOTALCOLIFORM':
                    if float(value) == 1:
                        newValid = 0

                elif (float(value) != -99) \
                        and (float(value) != -999) \
                        and element['name'] != 'ORP' \
                        and float(element['max']) == 0:
                    if float(value) < float(element['min']):
                        if float(value) >= (float(element['min']) * 0.75):
                            newValid = 1
                        else:
                            newValid = 0

                elif (float(value) != -99) \
                        and (float(value) != -999) \
                        and element['name'] != 'ORP' \
                        and (float(value) < float(element['min']) or
                             float(value) > float(element['max'])):
                    if float(value) >= (float(element['min']) * 0.75) and \
                            float(value) <= (float(element['max']) * 1.25):
                        newValid = 1
                    else:
                        newValid = 0

                if valid != newValid:
                    cur.execute("update element_reading set valid = %s where id = %s",
                                (newValid, id, ))

                    updateCount += 1

            mysql.connection.commit()
            cur.close()

            return jsonify({'msg': 'Success!', 'rows_updated': updateCount, 'element_id': elementId}), 200
        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            print(str(type(e).__name__) + ': ' + str(e))
            return jsonify({
                'msg': 'An error has occurred while processing the request.',
                'errorType': str(type(e).__name__),
                'error': str(e)}), 400

    @staticmethod
    def get_stations_records() -> dict:
        cursor = mysql.connection.cursor()

        getStationsQuery = "SELECT *, date_format(modified_time, '%Y-%m-%d %H:%i:%s') FROM site_master"

        cursor.execute(getStationsQuery)

        resultStations = cursor.fetchall()

        countStations = len(resultStations)

        data = []

        for stationRecord in resultStations:
            stationObject = {}

            stationObject['id'] = stationRecord[0]
            stationObject['unique_id'] = stationRecord[1]
            stationObject['village'] = stationRecord[2]
            stationObject['taluka'] = stationRecord[3]
            stationObject['district'] = stationRecord[4]
            stationObject['waterbody_name'] = stationRecord[5]
            stationObject['station_name'] = stationRecord[6]
            stationObject['lat'] = str(stationRecord[7])
            stationObject['lng'] = str(stationRecord[8])
            stationObject['category'] = stationRecord[9]
            stationObject['subdivision_name'] = stationRecord[10]
            stationObject['modified_time'] = stationRecord[12]

            data.append(stationObject)

        return {'data': data, 'count': countStations}

    @staticmethod
    def get_last_modified_time_of_stations() -> dict:
        cursor = mysql.connection.cursor()

        getLastModifiedTimeQuery = "select date_format(max(modified_time), '%Y-%m-%d %H:%i:%s') from site_master"

        cursor.execute(getLastModifiedTimeQuery)

        resultLastModifiedTime = cursor.fetchall()

        lastModifiedTime = ''

        if len(resultLastModifiedTime):
            lastModifiedTime = resultLastModifiedTime[0][0]

        return {'last_modified_time': lastModifiedTime}


class ClientMachine:
    def __init__(self, id, address, description, van_number):
        self.id = id
        self.address = address
        self.description = description
        self.van_number = van_number

    @ staticmethod
    def get_machines():
        cursor = mysql.connection.cursor()

        getMachinesQuery = "select * from client_machine;"
        # print(getmachinesQuery)
        cursor.execute(getMachinesQuery)

        results = cursor.fetchall()

        machines = None

        if len(results) > 0:
            # print(result[0][1])
            machines = [{
                'id': result[0],
                'address': result[1],
                'description':result[2],
                'van_number': result[3]
            } for result in results]

        # print(machines)
        cursor.close()
        return machines

    @ staticmethod
    def get_machine(id):
        cursor = mysql.connection.cursor()

        getMachinesQuery = "select * from client_machine where id=%s;"
        cursor.execute(getMachinesQuery, (id, ))

        results = cursor.fetchall()

        machine = None

        if len(results) > 0:
            # print(result[0][1])
            machine = {
                'id': results[0][0],
                'address': results[0][1],
                'description': results[0][2],
                'van_number': results[0][3]
            }

        cursor.close()
        return machine

    @ staticmethod
    def get_machine_by_address(address):
        cursor = mysql.connection.cursor()

        getMachinesQuery = "select * from client_machine where address=%s;"
        cursor.execute(getMachinesQuery, (address, ))

        results = cursor.fetchall()

        machine = None

        if len(results) > 0:
            # print(result[0][1])
            machine = {
                'id': results[0][0],
                'address': results[0][1],
                'description': results[0][2],
                'van_number': results[0][3]
            }

        cursor.close()
        return machine

    @ staticmethod
    def get_machine_by_address_not_id(address, id):
        cursor = mysql.connection.cursor()

        getMachinesQuery = "select * from client_machine where address='" + \
            address + "' and id<> '" + id + "';"
        cursor.execute(getMachinesQuery)

        results = cursor.fetchall()

        machine = None

        if len(results) > 0:
            # print(result[0][1])
            machine = {
                'id': results[0][0],
                'address': results[0][1],
                'description': results[0][2],
                'van_number': results[0][3]
            }

        cursor.close()
        return machine

    @ staticmethod
    def update_machine(machine):
        cursor = mysql.connection.cursor()

        updateMachinesQuery = "UPDATE client_machine SET address = %s, \
            description = %s, van_number=%s where id=%s;"
        # print(updateMachinesQuery)
        cursor.execute(updateMachinesQuery, (
            machine.address,
            machine.description.replace("\'", "\\'"),
            machine.van_number,
            machine.id))

        mysql.connection.commit()

        msg = 'Record updated.'

        cursor.close()
        return {'msg': msg}

    @ staticmethod
    def create_machine(address, description, van_number):
        cursor = mysql.connection.cursor()

        cursor.execute("INSERT INTO client_machine( \
                            address, \
                            description, \
                            van_number) \
                            VALUES \
                            (%s, %s, %s);", (address, description, van_number, ))
        mysql.connection.commit()
        cursor.close()

        return {'msg': 'Record added.'}

    @ staticmethod
    def delete_machine(id):
        cursor = mysql.connection.cursor()

        deleteMachinesQuery = "DELETE from client_machine where id='" + id + "';"
        # print(deleteMachinesQuery)
        cursor.execute(deleteMachinesQuery)

        mysql.connection.commit()
        cursor.close()

        msg = 'Record deleted.'

        return {'msg': msg}


class WaterBody:
    @ staticmethod
    def get_water_bodies_with_options(search: str, offset: int, limit: int) -> dict:
        cursor = mysql.connection.cursor()

        searchClause = ''

        if len(search) > 0:
            searchClause = "and (station_name like %s \
                            or district like %s \
                            or taluka like %s \
                            or subdivision_name like %s) "

        getWaterBodiesCountQuery = "SELECT count(id) from site_master where 1 = 1 \
                                    " + searchClause + ";"

        totalCount = 0
        if len(search) > 0:
            cursor.execute(getWaterBodiesCountQuery,
                           (search + '%%', search + '%%', search + '%%', search + '%%',))
        else:
            cursor.execute(getWaterBodiesCountQuery)
        results = cursor.fetchall()

        if len(results) > 0:
            totalCount = results[0][0]

        getWaterBodiesRecordsQuery = "select locations.*, count(distinct er.group_id) from \
                                    (SELECT id, unique_id, station_name, district, taluka, \
                                    subdivision_name FROM site_master \
                                    where 1 = 1 " + searchClause + " \
                                    limit " + str(limit) + " offset " + str(offset) + ") \
                                    locations left outer join \
                                    element_reading er on \
                                    locations.unique_id = er.station_id \
                                    group by locations.id;"

        if len(search) > 0:
            cursor.execute(getWaterBodiesRecordsQuery, (search + '%%',
                                                        search + '%%', search + '%%', search + '%%',))
        else:
            cursor.execute(getWaterBodiesRecordsQuery)

        results = cursor.fetchall()
        records = []

        for result in results:
            records.append({
                'id': result[0],
                'station_id': result[1],
                'waterbody_name': result[2],
                'district': result[3],
                'taluka': result[4],
                'region': result[5],
                'testing_count': result[6]
            })

        return {'records': records, 'totalCount': totalCount, 'count': len(results)}
