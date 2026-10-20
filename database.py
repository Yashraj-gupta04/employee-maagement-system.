import csv
import io
import sqlite3
from contextlib import closing

from employee import Employee


class DuplicateEmailError(Exception):
    """Raised when an email already exists in the database."""


SAMPLE_EMPLOYEES = [
    ("Aisha Khan", "aisha.khan@example.com", "Engineering", "Software Engineer", 85000),
    ("Bilal Ahmed", "bilal.ahmed@example.com", "Engineering", "Team Lead", 110000),
    ("Sara Ali", "sara.ali@example.com", "HR", "HR Manager", 70000),
    ("Omar Farooq", "omar.farooq@example.com", "Sales", "Sales Executive", 55000),
    ("Hina Malik", "hina.malik@example.com", "Marketing", "Designer", 60000),
    ("Zain Raza", "zain.raza@example.com", "Finance", "Accountant", 65000),
]


class EmployeeDatabase:
    def __init__(self, path="employees.db"):
        self.path = path
        self._create_table()

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_table(self):
        with closing(self._connect()) as conn, conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    department TEXT NOT NULL,
                    position TEXT NOT NULL,
                    salary REAL NOT NULL
                )
                """
            )

    @staticmethod
    def _to_employee(row):
        return Employee(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            department=row["department"],
            position=row["position"],
            salary=row["salary"],
        )

    def add(self, emp):
        emp.validate()
        try:
            with closing(self._connect()) as conn, conn:
                cur = conn.execute(
                    "INSERT INTO employees (name, email, department, position, salary) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (emp.name.strip(), emp.email.strip(), emp.department.strip(),
                     emp.position.strip(), emp.salary),
                )
                return cur.lastrowid
        except sqlite3.IntegrityError:
            raise DuplicateEmailError("An employee with this email already exists.")

    def get_all(self):
        with closing(self._connect()) as conn:
            rows = conn.execute("SELECT * FROM employees ORDER BY id").fetchall()
        return [self._to_employee(r) for r in rows]

    def search(self, term):
        like = f"%{term.strip()}%"
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT * FROM employees WHERE name LIKE ? OR email LIKE ? "
                "OR department LIKE ? OR position LIKE ? ORDER BY id",
                (like, like, like, like),
            ).fetchall()
        return [self._to_employee(r) for r in rows]

    def update(self, emp):
        if emp.id is None:
            raise ValueError("Employee id is required for update.")
        emp.validate()
        try:
            with closing(self._connect()) as conn, conn:
                conn.execute(
                    "UPDATE employees SET name=?, email=?, department=?, position=?, salary=? "
                    "WHERE id=?",
                    (emp.name.strip(), emp.email.strip(), emp.department.strip(),
                     emp.position.strip(), emp.salary, emp.id),
                )
        except sqlite3.IntegrityError:
            raise DuplicateEmailError("An employee with this email already exists.")

    def delete(self, emp_id):
        with closing(self._connect()) as conn, conn:
            cur = conn.execute("DELETE FROM employees WHERE id=?", (emp_id,))
            return cur.rowcount > 0

    def load_sample_data(self):
        added = 0
        for name, email, dept, pos, salary in SAMPLE_EMPLOYEES:
            try:
                self.add(Employee(name, email, dept, pos, salary))
                added += 1
            except DuplicateEmailError:
                pass
        return added

    def to_csv(self, employees=None):
        if employees is None:
            employees = self.get_all()
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["ID", "Name", "Email", "Department", "Position", "Salary"])
        for e in employees:
            writer.writerow([e.id, e.name, e.email, e.department, e.position, e.salary])
        return buffer.getvalue()