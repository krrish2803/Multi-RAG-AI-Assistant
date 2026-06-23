"""Tests for the custom exception hierarchy."""

from app.core.exceptions import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    ValidationError,
    GuardrailBlockedError,
    ServiceError,
)


def test_app_exception_defaults():
    exc = AppException(400, "test")
    assert exc.status_code == 400
    assert exc.detail == "test"


def test_authentication_error():
    exc = AuthenticationError()
    assert exc.status_code == 401
    assert exc.detail == "Invalid credentials"


def test_authorization_error():
    exc = AuthorizationError()
    assert exc.status_code == 403


def test_not_found_error():
    exc = NotFoundError("Document")
    assert exc.status_code == 404
    assert exc.detail == "Document not found"


def test_not_found_error_default():
    exc = NotFoundError()
    assert exc.detail == "Resource not found"


def test_conflict_error():
    exc = ConflictError()
    assert exc.status_code == 409


def test_validation_error():
    exc = ValidationError()
    assert exc.status_code == 422


def test_guardrail_blocked_error():
    exc = GuardrailBlockedError()
    assert exc.status_code == 400


def test_service_error():
    exc = ServiceError()
    assert exc.status_code == 500
