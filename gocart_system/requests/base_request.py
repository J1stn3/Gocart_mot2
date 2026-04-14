import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

class ValidationResult:
    """Structured result of validation operation."""
    def __init__(self, success: bool = True, validated_data: Optional[Dict[str, Any]] = None, errors: Optional[Dict[str, str]] = None):
        self.success = success
        self.validated_data = validated_data or {}
        self.errors = errors or {}

    @property
    def is_valid(self) -> bool:
        return self.success

    @property
    def data(self) -> Dict[str, Any]:
        return self.validated_data

    def add_error(self, field: str, message: str):
        """Add an error message to the result."""
        self.errors[field] = message
        self.success = False

    def set_data(self, key: str, value: Any):
        """Set validated data."""
        self.validated_data[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'success': self.success,
            'data': self.validated_data if self.success else None,
            'errors': self.errors
        }

class BaseRequest(ABC):
    """Base class for all request validation classes."""

    def __init__(self, data: Dict[str, Any]):
        self.raw_data = data
        self.result = ValidationResult()

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate the request data. Must be implemented by subclasses."""
        pass

    def validate_required(self, field: str, field_name: str) -> bool:
        """Validate that a field is present and not empty."""
        value = self.raw_data.get(field)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            self.result.add_error(field, f"{field_name} is required and cannot be empty.")
            return False
        self.result.set_data(field, value.strip() if isinstance(value, str) else value)
        return True

    def validate_string_length(self, field: str, field_name: str, min_length: int = 1, max_length: int = 255) -> bool:
        """Validate string field length."""
        if not self.validate_required(field, field_name):
            return False

        value = self.result.validated_data[field]
        if not isinstance(value, str):
            self.result.add_error(field, f"{field_name} must be a string.")
            return False

        if len(value) < min_length:
            self.result.add_error(field, f"{field_name} must be at least {min_length} characters long.")
            return False

        if len(value) > max_length:
            self.result.add_error(field, f"{field_name} cannot exceed {max_length} characters.")
            return False

        self.result.set_data(field, value.strip())
        return True

    def validate_email(self, field: str, field_name: str) -> bool:
        """Validate an email field format."""
        if not self.validate_required(field, field_name):
            return False

        value = self.result.validated_data[field]
        pattern = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
        if not pattern.match(value):
            self.result.add_error(field, f"{field_name} must be a valid email address.")
            return False

        self.result.set_data(field, value.strip())
        return True

    def validate_date(self, field: str, field_name: str, date_format: str = '%Y-%m-%d') -> bool:
        """Validate a date field with a specific format."""
        if not self.validate_required(field, field_name):
            return False

        value = self.result.validated_data[field]
        try:
            parsed_date = datetime.strptime(value, date_format)
            self.result.set_data(field, parsed_date.strftime(date_format))
            return True
        except (ValueError, TypeError):
            self.result.add_error(field, f"{field_name} must be a valid date in {date_format} format.")
            return False

    def validate_positive_number(self, field: str, field_name: str) -> bool:
        """Validate that a field is a positive number."""
        if not self.validate_required(field, field_name):
            return False

        try:
            value = float(self.result.validated_data[field])
            if value <= 0:
                self.result.add_error(field, f"{field_name} must be a positive number.")
                return False
            self.result.set_data(field, value)
            return True
        except (ValueError, TypeError):
            self.result.add_error(field, f"{field_name} must be a valid number.")
            return False

    def validate_positive_integer(self, field: str, field_name: str) -> bool:
        """Validate that a field is a positive integer."""
        if not self.validate_required(field, field_name):
            return False

        try:
            value = int(float(self.result.validated_data[field]))  # Handle string floats like "1.0"
            if value <= 0:
                self.result.add_error(field, f"{field_name} must be a positive integer.")
                return False
            self.result.set_data(field, value)
            return True
        except (ValueError, TypeError):
            self.result.add_error(field, f"{field_name} must be a valid integer.")
            return False

    def validate_non_negative_integer(self, field: str, field_name: str) -> bool:
        """Validate that a field is a non-negative integer (including 0)."""
        if not self.validate_required(field, field_name):
            return False

        try:
            value = int(float(self.result.validated_data[field]))
            if value < 0:
                self.result.add_error(field, f"{field_name} cannot be negative.")
                return False
            self.result.set_data(field, value)
            return True
        except (ValueError, TypeError):
            self.result.add_error(field, f"{field_name} must be a valid integer.")
            return False

    def validate_price(self, field: str, field_name: str) -> bool:
        """Validate price format (decimal with at most 2 places)."""
        if not self.validate_required(field, field_name):
            return False

        try:
            price = float(self.result.validated_data[field])
            if price < 0:
                self.result.add_error(field, f"{field_name} cannot be negative.")
                return False
            # Ensure it has at most 2 decimal places
            if round(price, 2) != price:
                self.result.add_error(field, f"{field_name} can have at most 2 decimal places.")
                return False
            self.result.set_data(field, price)
            return True
        except (ValueError, TypeError):
            self.result.add_error(field, f"{field_name} must be a valid price.")
            return False

    def validate_optional_string(self, field: str, field_name: str, max_length: int = 255) -> bool:
        """Validate optional string field."""
        value = self.raw_data.get(field)
        if value is not None:
            if not isinstance(value, str):
                self.result.add_error(field, f"{field_name} must be a string.")
                return False
            value = value.strip()
            if len(value) > max_length:
                self.result.add_error(field, f"{field_name} cannot exceed {max_length} characters.")
                return False
            self.result.set_data(field, value)
        return True