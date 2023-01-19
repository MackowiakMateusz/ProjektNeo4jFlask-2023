from flask import Flask, jsonify, request
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os #provides ways to access the Operating System and allows us to read the environment variables

load_dotenv()

app = Flask(__name__)

uri = "bolt://localhost:7687" #os.getenv('URI')
user = "neo4j"#os.getenv("USERNAME")
password = "test1234"#os.getenv("PASSWORD")
driver = GraphDatabase.driver(uri, auth=(user, password),database="neo4j")
#(15%) Stwórz w bazie danych neo4j labele Employee i Department oraz relacje WORKS_IN i MANAGES.
# Dodaj do bazy danych wiele węzłów pracowników i departamentów oraz połącz je odpowiednimi relacjami.
# komentarz o zawartosci: "koniec podpunktu 1" konczy kod do tego podpunktu
def get_employees(tx):
    query = "MATCH (m:Employee) RETURN m"
    results = tx.run(query).data()
    employees = [{'name': result['m']['name'], 'hired_in_year': result['m']['hired_in_year']} for result in results]
    return employees

@app.route('/employees', methods=['GET'])
def get_employees_route():
    with driver.session() as session:
        employees = session.read_transaction(get_employees)

    response = {'employees': employees}
    return jsonify(response)

def get_employee(tx, name):
    query = "MATCH (m:Employee) WHERE m.name=$name RETURN m"
    result = tx.run(query, name=name).data()

    if not result:
        return None
    else:
        return {'name': result[0]['m']['name'], 'hired_in_year': result[0]['m']['hired_in_year']}

@app.route('/employees/<string:name>', methods=['GET'])
def get_employee_route(name):
    with driver.session() as session:
        employee = session.read_transaction(get_employee, name)

    if not employee:
        response = {'message': 'Employee not found'}
        return jsonify(response), 404
    else:
        response = {'employee': employee}
        return jsonify(response)

def add_employee(tx, name, year):
    query = "CREATE (m:Employee {name: $name, hired_in_year: $hired_in_year})"
    tx.run(query, name=name, hired_in_year=year)


@app.route('/employees', methods=['POST'])
def add_employee_route():
    name = request.json['name']
    year = request.json['hired_in_year']

    with driver.session() as session:
        session.write_transaction(add_employee, name, year)

    response = {'status': 'success'}
    return jsonify(response)


def update_employee(tx, name, new_name, new_year):
    query = "MATCH (m:Employee) WHERE m.name=$name RETURN m"
    result = tx.run(query, name=name).data()

    if not result:
        return None
    else:
        query = "MATCH (m:Employee) WHERE m.name=$name SET m.name=$new_name, m.hired_in_year=$new_year"
        tx.run(query, name=name, new_name=new_name, new_year=new_year)
        return {'name': new_name, 'year': new_year}


@app.route('/employees/<string:name>', methods=['PUT'])
def update_employee_route(name):
    new_name = request.json['name']
    new_year = request.json['hired_in_year']

    with driver.session() as session:
        employee = session.write_transaction(update_employee, name, new_name, new_year)

    if not employee:
        response = {'message': 'Employee not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_employee(tx, name):
    query = "MATCH (m:Employee) WHERE m.name=$name RETURN m"
    result = tx.run(query, name=name).data()

    if not result:
        return None
    else:
        query = "MATCH (m:Employee) WHERE m.name=$name DETACH DELETE m"
        tx.run(query, name=name)
        return {'name': name}

@app.route('/employees/<string:name>', methods=['DELETE'])
def delete_employee_route(name):
    with driver.session() as session:
        employee = session.write_transaction(delete_employee, name)

    if not employee:
        response = {'message': 'Employee not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)

#=========================================================DEPARTMENTS===================================================
def get_departments(tx):
    query = "MATCH (m:Department) RETURN m"
    results = tx.run(query).data()
    departments = [{'name': result['m']['name'], 'established_in_year': result['m']['established_in_year']} for result in results]
    return departments

@app.route('/departments', methods=['GET'])
def get_departments_route():
    with driver.session() as session:
        departments = session.read_transaction(get_departments)

    response = {'departments': departments}
    return jsonify(response)

def get_department(tx, name):
    query = "MATCH (m:Department) WHERE m.name=$name RETURN m"
    result = tx.run(query, name=name).data()

    if not result:
        return None
    else:
        return {'name': result[0]['m']['name'], 'established_in_year': result[0]['m']['established_in_year']}

@app.route('/departments/<string:name>', methods=['GET'])
def get_department_route(name):
    with driver.session() as session:
        department = session.read_transaction(get_department, name)

    if not department:
        response = {'message': 'Department not found'}
        return jsonify(response), 404
    else:
        response = {'department': department}
        return jsonify(response)

def add_department(tx, name, year):
    query = "CREATE (m:Department {name: $name, established_in_year: $established_in_year})"
    tx.run(query, name=name, established_in_year=year)


@app.route('/departments', methods=['POST'])
def add_department_route():
    name = request.json['name']
    year = request.json['established_in_year']

    with driver.session() as session:
        session.write_transaction(add_department, name, year)

    response = {'status': 'success'}
    return jsonify(response)


def update_department(tx, name, new_name, new_year):
    query = "MATCH (m:Department) WHERE m.name=$name RETURN m"
    result = tx.run(query, name=name).data()

    if not result:
        return None
    else:
        query = "MATCH (m:Department) WHERE m.name=$name SET m.name=$new_name, m.established_in_year=$new_year"
        tx.run(query, name=name, new_name=new_name, new_year=new_year)
        return {'name': new_name, 'year': new_year}


@app.route('/departments/<string:name>', methods=['PUT'])
def update_department_route(name):
    new_name = request.json['name']
    new_year = request.json['established_in_year']

    with driver.session() as session:
        department = session.write_transaction(update_department, name, new_name, new_year)

    if not department:
        response = {'message': 'Department not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_department(tx, name):
    query = "MATCH (m:Department) WHERE m.name=$name RETURN m"
    result = tx.run(query, name=name).data()

    if not result:
        return None
    else:
        query = "MATCH (m:Department) WHERE m.name=$name DETACH DELETE m"
        tx.run(query, name=name)
        return {'name': name}

@app.route('/departments/<string:name>', methods=['DELETE'])
def delete_department_route(name):
    with driver.session() as session:
        department = session.write_transaction(delete_department, name)

    if not department:
        response = {'message': 'Department not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)
#=====================================laczenie relacjami========================================
def connect_by_WORKS_IN(tx, employee_id,department_id):
    query = "MATCH (employee:Employee), (department:Department) WHERE ID(employee)=employee_id AND ID(department)=$department_id RETURN employee.name,department.name"
    result = tx.run(query, employee_id=employee_id,department_id=department_id).data()
    #to powyzej sprawdza czy w bazie istnieja takie obiekty z takimi idkami
    if not result:
        return None
    else:# a tutaj robi relacje
        query = "MATCH (employee:Employee), (department:Department) WHERE ID(employee)=employee_id AND ID(department)=$department_id CREATE (employee)-[works_in:WORKS_IN]->(department)"
        tx.run(query, name=name)
        return {'name': name}

@app.route('/employees/add_relation_subservient_to_department/WORKS_IN/<string:employee_id>/<string:department_id>', methods=['POST'])
def add_relation_subservient_to_department_WORKS_IN(employee_id,department_id):
    with driver.session() as session:
        department = session.write_transaction(connect_by_WORKS_IN, employee_id,department_id)

    if not department:
        response = {'message': 'Department not found with this id or Employee not found with this id'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)

def connect_by_MANAGES(tx, employee_id,department_id):
    query = "MATCH (employee:Employee), (department:Department) WHERE ID(employee)=employee_id AND ID(department)=$department_id RETURN employee.name,department.name"
    result = tx.run(query, employee_id=employee_id,department_id=department_id).data()
    #to powyzej sprawdza czy w bazie istnieja takie obiekty z takimi idkami
    if not result:
        return None
    else:# a tutaj robi relacje
        query = "MATCH (employee:Employee), (department:Department) WHERE ID(employee)=employee_id AND ID(department)=$department_id CREATE (employee)-[manages:MANAGES]->(department)"
        tx.run(query, name=name)
        return {'name': name}

@app.route('/employees/add_relation_subservient_to_department/MANAGES/<string:employee_id>/<string:department_id>', methods=['POST'])
def add_relation_subservient_to_department_MANAGES(employee_id,department_id):
    with driver.session() as session:
        department = session.write_transaction(connect_by_WORKS_IN, employee_id,department_id)

    if not department:
        response = {'message': 'Department not found with this id or Employee not found with this id'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)
#Koniec podpunktu 1

if __name__ == '__main__':
    app.run()

