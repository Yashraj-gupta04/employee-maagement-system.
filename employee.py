import re
from dataclasses import dataclass
from typing import Optional

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Employee:
    name: str
    email: str
    department: str
    position: str
    salary: float
    id: Optional[int] = None

    def validate(self):
        """Raise ValueError if any field is invalid."""
        if not self.name.strip():
            raise ValueError("Name is required.")
        if not EMAIL_PATTERN.match(self.email.strip()):
            raise ValueError("Enter a valid email address.")
        if not self.department.strip():
            raise ValueError("Department is required.")
        if not self.position.strip():
            raise ValueError("Position is required.")
        if self.salary < 0:
            raise ValueError("Salary cannot be negative.")