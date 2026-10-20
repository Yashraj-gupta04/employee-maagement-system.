import pytest

from database import DuplicateEmailError, EmployeeDatabase
from employee import Employee


@pytest.fixture
def db(tmp_path):
    return EmployeeDatabase(str(tmp_path / "test.db"))


def make(email="a@example.com"):
    return Employee("Ann", email, "IT", "Developer", 50000)


def test_add_and_get(db):
    db.add(make())
    people = db.get_all()
    assert len(people) == 1
    assert people[0].name == "Ann"


def test_duplicate_email_rejected(db):
    db.add(make())
    with pytest.raises(DuplicateEmailError):
        db.add(make("A@example.com"))


def test_invalid_email(db):
    with pytest.raises(ValueError):
        db.add(make("not-an-email"))


def test_negative_salary(db):
    bad = Employee("Ann", "a@example.com", "IT", "Dev", -5)
    with pytest.raises(ValueError):
        db.add(bad)


def test_search(db):
    db.add(make("a@example.com"))
    db.add(Employee("Bob", "b@example.com", "HR", "Manager", 60000))
    assert len(db.search("HR")) == 1
    assert len(db.search("example")) == 2


def test_update(db):
    emp_id = db.add(make())
    db.update(Employee("Ann Lee", "a@example.com", "IT", "Senior", 70000, id=emp_id))
    assert db.get_all()[0].name == "Ann Lee"


def test_delete(db):
    emp_id = db.add(make())
    assert db.delete(emp_id) is True
    assert db.get_all() == []


def test_sample_data_and_csv(db):
    assert db.load_sample_data() == 6
    assert db.load_sample_data() == 0
    assert db.to_csv().startswith("ID,Name,Email")