from . import mysql
from flask import Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
import base64
import io
from PIL import Image

model = Blueprint('model', __name__)

totalColiformStatus = ['Absent', 'Present', 'Not Tested']


def get_reading_value_status_by_element(element, value):
    reading_value = value
    if value == -99:
        reading_value = 'N/A'
    elif value == -999:
        reading_value = 'Result Awaiting'
    elif element == 'TOTALCOLIFORM' and value >= 0 and value <= 2:
        reading_value = totalColiformStatus[int(value)]

    return reading_value


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
        return self.admin == 1

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
                                       'max': result[4], 'unit': result[2]}

        # print(elements)
        cursor.close()
        return elements

    @staticmethod
    def get_element_readings_dict(group_id):
        cursor = mysql.connection.cursor()

        getReadingsQuery = "SELECT element_name, reading_value FROM element_reading where group_id = " + group_id
        cursor.execute(getReadingsQuery)

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

        getReadingsQuery = "SELECT element_name, reading_value FROM element_reading where group_id = " + \
            group_id + " order by id;"

        cursor.execute(getReadingsQuery)

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

        getGroupRecordsQuery = "select distinct group_id, date_format(reading_time, '%Y-%m-%d %H:%i:%s'), \
                                location, lat, lng, station_id, waterbody_name \
                                from element_reading where date(reading_time) >= '" + start + "' and \
                                date(reading_time) <= '" + end + "' order by group_id;"

        # print(getGroupRecordsQuery)

        cursor.execute(getGroupRecordsQuery)

        resultGroupRecords = cursor.fetchall()
        recordLength = len(resultGroupRecords)
        dictElements = Element.get_elements_dict()
        data = []

        for groupRecord in resultGroupRecords:
            dataObject = {}
            groupId = groupRecord[0]
            dataObject['group_id'] = int(groupId)
            dataObject['reading_time'] = groupRecord[1]
            dataObject['location'] = groupRecord[2]
            dataObject['latitude'] = str(groupRecord[3])
            dataObject['longitude'] = str(groupRecord[4])
            dataObject['station_id'] = groupRecord[5]
            dataObject['waterbody_name'] = groupRecord[6]

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


class ClientMachine:
    def __init__(self, id, address, description):
        self.id = id
        self.address = address
        self.description = description

    @staticmethod
    def get_machines():
        cursor = mysql.connection.cursor()

        getMachinesQuery = "select * from client_machine;"
        # print(getmachinesQuery)
        cursor.execute(getMachinesQuery)

        results = cursor.fetchall()

        machines = None

        if len(results) > 0:
            # print(result[0][1])
            machines = [{'id': result[0], 'address': result[1],
                         'description':result[2]} for result in results]

        # print(machines)
        cursor.close()
        return machines

    @staticmethod
    def get_machine(id):
        cursor = mysql.connection.cursor()

        getMachinesQuery = "select * from client_machine where id='" + id + "';"
        cursor.execute(getMachinesQuery)

        results = cursor.fetchall()

        machine = None

        if len(results) > 0:
            # print(result[0][1])
            machine = {'id': results[0][0], 'address': results[0][1],
                       'description': results[0][2]}

        cursor.close()
        return machine

    @staticmethod
    def get_machine_by_address(address):
        cursor = mysql.connection.cursor()

        getMachinesQuery = "select * from client_machine where address='" + \
            address + "';"
        cursor.execute(getMachinesQuery)

        results = cursor.fetchall()

        machine = None

        if len(results) > 0:
            # print(result[0][1])
            machine = {'id': results[0][0], 'address': results[0][1],
                       'description': results[0][2]}

        cursor.close()
        return machine

    @staticmethod
    def get_machine_by_address_not_id(address, id):
        cursor = mysql.connection.cursor()

        getMachinesQuery = "select * from client_machine where address='" + \
            address + "' and id<> '" + id + "';"
        cursor.execute(getMachinesQuery)

        results = cursor.fetchall()

        machine = None

        if len(results) > 0:
            # print(result[0][1])
            machine = {'id': results[0][0], 'address': results[0][1],
                       'description': results[0][2]}

        cursor.close()
        return machine

    @staticmethod
    def update_machine(machine):
        cursor = mysql.connection.cursor()

        updateMachinesQuery = "UPDATE client_machine SET address = '" + machine.address + \
            "', description = '" + \
            machine.description.replace(
                "\'", "\\'") + "' where id='" + machine.id + "';"
        # print(updateMachinesQuery)
        cursor.execute(updateMachinesQuery)

        mysql.connection.commit()

        msg = 'Record updated.'

        cursor.close()
        return {'msg': msg}

    @staticmethod
    def create_machine(address, description):
        cursor = mysql.connection.cursor()

        cursor.execute("INSERT INTO client_machine( \
                            address, \
                            description) \
                            VALUES \
                            (%s, %s);", (address, description))
        mysql.connection.commit()
        cursor.close()

        return {'msg': 'Record added.'}

    @staticmethod
    def delete_machine(id):
        cursor = mysql.connection.cursor()

        deleteMachinesQuery = "DELETE from client_machine where id='" + id + "';"
        # print(deleteMachinesQuery)
        cursor.execute(deleteMachinesQuery)

        mysql.connection.commit()
        cursor.close()

        msg = 'Record deleted.'

        return {'msg': msg}
