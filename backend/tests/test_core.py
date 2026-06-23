"""Tests for core RBAC and security modules."""

from app.core.rbac import (
    get_accessible_departments,
    get_accessible_sensitivity,
    check_role_permission,
    is_admin,
    ROLE_ACCESS_MATRIX,
    SENSITIVITY_ACCESS,
)
from app.models.user import Role
from app.core.security import hash_password, verify_password


def test_roles_exist():
    assert len(Role) >= 5
    assert Role.ADMIN.value == "admin"
    assert Role.EMPLOYEE.value == "employee"


def test_role_access_matrix_has_all_roles():
    for role in Role:
        assert role in ROLE_ACCESS_MATRIX, f"Role {role} missing from access matrix"


def test_sensitivity_access_has_all_roles():
    for role in Role:
        assert role in SENSITIVITY_ACCESS, f"Role {role} missing from sensitivity access"


def test_get_accessible_departments():
    depts = get_accessible_departments(Role.ADMIN)
    assert "company-wide" in depts
    assert "hr" in depts
    assert "engineering" in depts


def test_get_accessible_departments_employee():
    depts = get_accessible_departments(Role.EMPLOYEE)
    assert "company-wide" in depts
    assert "hr" not in depts


def test_get_accessible_departments_with_custom():
    depts = get_accessible_departments(Role.EMPLOYEE, ["engineering"])
    assert "company-wide" in depts
    assert "engineering" in depts


def test_get_accessible_sensitivity_admin():
    access = get_accessible_sensitivity(Role.ADMIN)
    assert "restricted" in access
    assert "public" in access


def test_get_accessible_sensitivity_employee():
    access = get_accessible_sensitivity(Role.EMPLOYEE)
    assert "public" in access
    assert "internal" in access
    assert "confidential" not in access


def test_check_role_permission():
    assert check_role_permission(Role.ADMIN, [Role.ADMIN])
    assert not check_role_permission(Role.EMPLOYEE, [Role.ADMIN])


def test_is_admin():
    assert is_admin(Role.ADMIN)
    assert not is_admin(Role.EMPLOYEE)
    assert not is_admin(Role.HR)


def test_password_hashing():
    password = "test_password_123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_password_hashing_different():
    password = "test_password_123"
    hashed1 = hash_password(password)
    hashed2 = hash_password(password)
    assert hashed1 != hashed2  # bcrypt uses different salts


def test_wrong_password():
    hashed = hash_password("correct_password")
    assert not verify_password("wrong_password", hashed)
