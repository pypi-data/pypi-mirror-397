"""
MedhaOne Access Control Time Constraints

Time constraint evaluation for access rules.
Supports date ranges, time windows, and day-of-week restrictions.
"""

from datetime import datetime, time, date, timezone
from typing import Dict, Optional, Any, Tuple, List

from medha_one_access.core.exceptions import TimeConstraintError


class TimeConstraintEvaluator:
    """Evaluator for time constraints on access rules."""

    @staticmethod
    def is_satisfied(
        constraint: Optional[Dict[str, Any]], evaluation_time: Optional[datetime] = None
    ) -> bool:
        """
        Check if all time constraints are satisfied.

        Args:
            constraint: Time constraint dictionary
            evaluation_time: Time to evaluate constraints against (defaults to current time)

        Returns:
            True if constraints are satisfied or if there are no constraints

        Raises:
            TimeConstraintError: If constraint format is invalid
        """
        if not constraint:
            return True

        # Use current time if not specified
        evaluation_time = evaluation_time or datetime.now(timezone.utc)

        try:
            # Check date range
            if not TimeConstraintEvaluator._check_date_range(
                constraint, evaluation_time
            ):
                return False

            # Check days of week
            if not TimeConstraintEvaluator._check_days_of_week(
                constraint, evaluation_time
            ):
                return False

            # Check time window
            if not TimeConstraintEvaluator._check_time_window(
                constraint, evaluation_time
            ):
                return False

            # All constraints satisfied
            return True

        except Exception as e:
            raise TimeConstraintError(
                constraint, f"Error evaluating time constraint: {str(e)}"
            )

    @staticmethod
    def _check_date_range(
        constraint: Dict[str, Any], evaluation_time: datetime
    ) -> bool:
        """
        Check if the evaluation time falls within the date range constraints.

        Args:
            constraint: Time constraint dictionary
            evaluation_time: Time to check

        Returns:
            True if date range constraints are satisfied
        """
        current_date = evaluation_time.date()

        # Check start date
        if constraint.get("startDate"):
            start_date = _parse_date(constraint["startDate"])
            if current_date < start_date:
                return False

        # Check end date
        if constraint.get("endDate"):
            end_date = _parse_date(constraint["endDate"])
            if current_date > end_date:
                return False

        return True

    @staticmethod
    def _check_days_of_week(
        constraint: Dict[str, Any], evaluation_time: datetime
    ) -> bool:
        """
        Check if the evaluation time falls on an allowed day of the week.

        Args:
            constraint: Time constraint dictionary
            evaluation_time: Time to check

        Returns:
            True if day-of-week constraints are satisfied
        """
        if "daysOfWeek" not in constraint or not constraint["daysOfWeek"]:
            return True

        # Get current day of week (0=Sunday, 6=Saturday)
        current_day = evaluation_time.weekday()

        # Convert to same format (Python uses 0=Monday, 6=Sunday)
        # Convert to 0=Sunday, 6=Saturday format
        if current_day == 6:  # Sunday in Python is 6
            current_day = 0
        else:
            current_day += 1

        return current_day in constraint["daysOfWeek"]

    @staticmethod
    def _check_time_window(
        constraint: Dict[str, Any], evaluation_time: datetime
    ) -> bool:
        """
        Check if the evaluation time falls within the time window constraints.

        Args:
            constraint: Time constraint dictionary
            evaluation_time: Time to check

        Returns:
            True if time window constraints are satisfied
        """
        if not constraint.get("startTime") or not constraint.get("endTime"):
            return True

        # Parse time strings
        start_time = _parse_time(constraint["startTime"])
        end_time = _parse_time(constraint["endTime"])
        current_time = evaluation_time.time()

        # Handle overnight time windows (e.g., 22:00 to 06:00)
        if start_time > end_time:
            # Time window spans midnight
            return current_time >= start_time or current_time <= end_time
        else:
            # Normal time window within same day
            return start_time <= current_time <= end_time

    @staticmethod
    def validate_constraint(constraint: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a time constraint dictionary for correct format and values.

        Args:
            constraint: Time constraint to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not constraint:
            return True, None

        try:
            # Validate date format
            if "startDate" in constraint:
                try:
                    _parse_date(constraint["startDate"])
                except Exception:
                    return False, f"Invalid startDate format: {constraint['startDate']}"

            if "endDate" in constraint:
                try:
                    _parse_date(constraint["endDate"])
                except Exception:
                    return False, f"Invalid endDate format: {constraint['endDate']}"

            # Validate date range logic
            if "startDate" in constraint and "endDate" in constraint:
                start_date = _parse_date(constraint["startDate"])
                end_date = _parse_date(constraint["endDate"])
                if start_date > end_date:
                    return False, "startDate cannot be after endDate"

            # Validate time format
            if "startTime" in constraint:
                try:
                    _parse_time(constraint["startTime"])
                except Exception:
                    return False, f"Invalid startTime format: {constraint['startTime']}"

            if "endTime" in constraint:
                try:
                    _parse_time(constraint["endTime"])
                except Exception:
                    return False, f"Invalid endTime format: {constraint['endTime']}"

            # Validate days of week
            if "daysOfWeek" in constraint:
                days = constraint["daysOfWeek"]
                if not isinstance(days, list):
                    return False, "daysOfWeek must be a list"

                for day in days:
                    if not isinstance(day, int) or day < 0 or day > 6:
                        return (
                            False,
                            f"Invalid day of week: {day}. Must be integer 0-6 (0=Sunday)",
                        )

            return True, None

        except Exception as e:
            return False, f"Error validating constraint: {str(e)}"

    @staticmethod
    def get_next_allowed_time(
        constraint: Dict[str, Any], current_time: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Get the next time when the constraint would be satisfied.

        Args:
            constraint: Time constraint dictionary
            current_time: Current time (defaults to now)

        Returns:
            Next datetime when constraint is satisfied, or None if never satisfied
        """
        if not constraint:
            return current_time or datetime.now(timezone.utc)

        current_time = current_time or datetime.now(timezone.utc)

        # For simplicity, this is a basic implementation
        # A full implementation would calculate the exact next allowed time
        # considering all constraint combinations

        # Check if currently satisfied
        if TimeConstraintEvaluator.is_satisfied(constraint, current_time):
            return current_time

        # For now, return None if not currently satisfied
        # TODO: Implement full next-time calculation logic
        return None


def _parse_date(date_str: str) -> date:
    """
    Parse ISO format date string to date object.

    Args:
        date_str: Date string in ISO format (YYYY-MM-DD)

    Returns:
        Parsed date object
    """
    if isinstance(date_str, str):
        return datetime.fromisoformat(date_str).date()
    return date_str


def _parse_time(time_str: str) -> time:
    """
    Parse HH:MM format time string to time object.

    Args:
        time_str: Time string in HH:MM format

    Returns:
        Parsed time object
    """
    if isinstance(time_str, str):
        hours, minutes = map(int, time_str.split(":"))
        return time(hour=hours, minute=minutes)
    return time_str


# Export classes
__all__ = [
    "TimeConstraintEvaluator",
]
