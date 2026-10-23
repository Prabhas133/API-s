
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "employees.json"
)


def read_employees():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_employees(employees):
    temp_file = DATA_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(employees, file, indent=4)

    os.replace(temp_file, DATA_FILE)


def find_employee(employees, employee_id):
    return next(
        (e for e in employees if e["id"] == employee_id),
        None
    )


def format_employee(employee, employees):
    manager_id = employee.get("manager_id")
    manager = (
        find_employee(employees, manager_id)
        if manager_id is not None else None
    )

    result = employee.copy()
    result["manager"] = (
        {
            "id": manager["id"],
            "name": manager["name"],
            "designation": manager["designation"],
            "department": manager["department"]
        }
        if manager else None
    )

    return result


# GET: All employees
@app.route("/employees", methods=["GET"])
def get_employees():
    employees = read_employees()
    return jsonify([
        format_employee(e, employees) for e in employees
    ]), 200


# GET: One employee
@app.route("/employees/<int:employee_id>", methods=["GET"])
def get_employee(employee_id):
    employees = read_employees()
    employee = find_employee(employees, employee_id)

    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify(format_employee(employee, employees)), 200


# GET: Manager of one employee
@app.route("/employees/<int:employee_id>/manager", methods=["GET"])
def get_manager(employee_id):
    employees = read_employees()
    employee = find_employee(employees, employee_id)

    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    manager_id = employee.get("manager_id")

    if manager_id is None:
        return jsonify({"message": "No manager assigned"}), 200

    manager = find_employee(employees, manager_id)

    if manager is None:
        return jsonify({"error": "Manager not found"}), 404

    return jsonify(format_employee(manager, employees)), 200


# GET: Employees reporting to a manager
@app.route("/managers/<int:manager_id>/employees", methods=["GET"])
def get_team(manager_id):
    employees = read_employees()
    manager = find_employee(employees, manager_id)

    if manager is None:
        return jsonify({"error": "Manager not found"}), 404

    team = [
        format_employee(e, employees)
        for e in employees
        if e.get("manager_id") == manager_id
    ]

    return jsonify({
        "manager": format_employee(manager, employees),
        "employees": team
    }), 200


# POST: Add an employee
@app.route("/employees", methods=["POST"])
def add_employee():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400

    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name is required"}), 400

    employees = read_employees()
    manager_id = data.get("manager_id")

    if manager_id is not None:
        if (
            not isinstance(manager_id, int)
            or isinstance(manager_id, bool)
        ):
            return jsonify({"error": "Invalid manager ID"}), 400

        if find_employee(employees, manager_id) is None:
            return jsonify({"error": "Manager not found"}), 400

    new_employee = {
        "id": max((e["id"] for e in employees), default=0) + 1,
        "name": name.strip(),
        "age": data.get("age"),
        "gender": data.get("gender"),
        "email": data.get("email"),
        "department": data.get("department"),
        "designation": data.get("designation"),
        "salary": data.get("salary"),
        "manager_id": manager_id
    }

    employees.append(new_employee)
    save_employees(employees)

    return jsonify(format_employee(new_employee, employees)), 201


# PUT: Update an employee
@app.route("/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    employees = read_employees()
    employee = find_employee(employees, employee_id)

    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return jsonify({"error": "Invalid name"}), 400
        employee["name"] = data["name"].strip()

    if "manager_id" in data:
        manager_id = data["manager_id"]

        if manager_id == employee_id:
            return jsonify({"error": "Cannot manage yourself"}), 400

        if manager_id is not None:
            if (
                not isinstance(manager_id, int)
                or isinstance(manager_id, bool)
            ):
                return jsonify({"error": "Invalid manager ID"}), 400

            if find_employee(employees, manager_id) is None:
                return jsonify({"error": "Manager not found"}), 400

            # Prevent circular reporting relationships.
            current_id = manager_id

            while current_id is not None:
                if current_id == employee_id:
                    return jsonify({
                        "error": "Circular manager relationship"
                    }), 400

                current = find_employee(employees, current_id)
                current_id = (
                    current.get("manager_id") if current else None
                )

    for field in [
        "age", "gender", "email", "department",
        "designation", "salary"
    ]:
        if field in data:
            employee[field] = data[field]

    if "manager_id" in data:
        employee["manager_id"] = data["manager_id"]

    save_employees(employees)
    return jsonify(format_employee(employee, employees)), 200


# DELETE: Delete an employee
@app.route("/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    employees = read_employees()
    employee = find_employee(employees, employee_id)

    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    # Remove references to the deleted manager.
    for e in employees:
        if e.get("manager_id") == employee_id:
            e["manager_id"] = None

    employees = [
        e for e in employees if e["id"] != employee_id
    ]

    save_employees(employees)

    return jsonify({
        "message": "Employee deleted successfully"
    }), 200


if __name__ == "__main__":
    app.run(debug=True,use_reloader=True)
