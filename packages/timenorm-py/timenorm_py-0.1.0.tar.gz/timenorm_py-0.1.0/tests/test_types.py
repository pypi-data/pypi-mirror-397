"""
Unit tests for core temporal types (Interval, Period, Repeating, Unit).
"""
import datetime
import pytest
from timenorm import (
    Interval,
    Period,
    PeriodSum,
    Repeating,
    Year,
    Unit,
    YEAR,
    MONTH,
    DAY,
    WEEK,
    HOUR,
    MINUTE,
    SECOND,
)


class TestInterval:
    """Tests for the Interval class."""

    def test_interval_of_year(self):
        """Test creating an interval for a full year."""
        interval = Interval.of(2024)
        assert interval.start == datetime.datetime(2024, 1, 1, 0, 0)
        assert interval.end == datetime.datetime(2025, 1, 1, 0, 0)

    def test_interval_of_month(self):
        """Test creating an interval for a full month."""
        interval = Interval.of(2024, 3)
        assert interval.start == datetime.datetime(2024, 3, 1, 0, 0)
        assert interval.end == datetime.datetime(2024, 4, 1, 0, 0)

    def test_interval_of_day(self):
        """Test creating an interval for a full day."""
        interval = Interval.of(2024, 3, 15)
        assert interval.start == datetime.datetime(2024, 3, 15, 0, 0)
        assert interval.end == datetime.datetime(2024, 3, 16, 0, 0)

    def test_interval_of_hour(self):
        """Test creating an interval for a full hour."""
        interval = Interval.of(2024, 3, 15, 14)
        assert interval.start == datetime.datetime(2024, 3, 15, 14, 0)
        assert interval.end == datetime.datetime(2024, 3, 15, 15, 0)

    def test_interval_fromisoformat(self):
        """Test creating an interval from ISO format strings."""
        interval = Interval.fromisoformat("2024-01-01 2024-02-01")
        assert interval.start == datetime.datetime(2024, 1, 1)
        assert interval.end == datetime.datetime(2024, 2, 1)

    def test_interval_is_defined(self):
        """Test checking if an interval is defined."""
        defined = Interval.of(2024)
        assert defined.is_defined()

        undefined = Interval(None, None)
        assert not undefined.is_defined()


class TestPeriod:
    """Tests for the Period class."""

    def test_period_addition(self):
        """Test adding a period to a datetime."""
        period = Period(MONTH, 3)
        start = datetime.datetime(2024, 1, 1)
        interval = start + period

        assert interval.start == datetime.datetime(2024, 1, 1)
        assert interval.end == datetime.datetime(2024, 4, 1)

    def test_period_subtraction(self):
        """Test subtracting a period from a datetime."""
        period = Period(DAY, 7)
        end = datetime.datetime(2024, 1, 15)
        interval = end - period

        assert interval.start == datetime.datetime(2024, 1, 8)
        assert interval.end == datetime.datetime(2024, 1, 15)

    def test_period_weeks(self):
        """Test period with weeks unit."""
        period = Period(WEEK, 2)
        start = datetime.datetime(2024, 1, 1)
        interval = start + period

        assert interval.start == datetime.datetime(2024, 1, 1)
        assert interval.end == datetime.datetime(2024, 1, 15)


class TestPeriodSum:
    """Tests for the PeriodSum class."""

    def test_period_sum_addition(self):
        """Test adding a sum of periods to a datetime."""
        period_sum = PeriodSum([Period(YEAR, 2), Period(DAY, 1)])
        start = datetime.datetime(2024, 1, 1)
        interval = start + period_sum

        assert interval.start == datetime.datetime(2024, 1, 1)
        assert interval.end == datetime.datetime(2026, 1, 2)


class TestRepeating:
    """Tests for the Repeating class."""

    def test_repeating_day_of_week(self):
        """Test repeating interval for a day of the week (Tuesday = 1)."""
        # Tuesday in dateutil is 1 (Monday=0)
        tuesday = Repeating(DAY, WEEK, value=1)
        anchor = datetime.datetime(2024, 11, 15)  # Friday

        # Next Tuesday after Friday Nov 15
        interval = anchor + tuesday
        assert interval.start == datetime.datetime(2024, 11, 19)  # Next Tuesday
        assert interval.end == datetime.datetime(2024, 11, 20)

    def test_repeating_month_of_year(self):
        """Test repeating interval for a month of the year (March = 3)."""
        march = Repeating(MONTH, YEAR, value=3)
        anchor = datetime.datetime(2024, 11, 15)

        # Next March after November
        interval = anchor + march
        assert interval.start == datetime.datetime(2025, 3, 1)
        assert interval.end == datetime.datetime(2025, 4, 1)

    def test_repeating_last(self):
        """Test finding last occurrence of a repeating interval."""
        tuesday = Repeating(DAY, WEEK, value=1)
        anchor = datetime.datetime(2024, 11, 15)  # Friday

        # Last Tuesday before Friday Nov 15
        interval = anchor - tuesday
        assert interval.start == datetime.datetime(2024, 11, 12)  # Previous Tuesday
        assert interval.end == datetime.datetime(2024, 11, 13)


class TestYear:
    """Tests for the Year class."""

    def test_year_basic(self):
        """Test basic year interval."""
        year = Year(2024)
        assert year.start == datetime.datetime(2024, 1, 1)
        assert year.end == datetime.datetime(2025, 1, 1)

    def test_year_decade(self):
        """Test year with decade (missing 1 digit)."""
        decade = Year(198, n_missing_digits=1)  # 1980s
        assert decade.start == datetime.datetime(1980, 1, 1)
        assert decade.end == datetime.datetime(1990, 1, 1)

    def test_year_century(self):
        """Test year with century (missing 2 digits)."""
        century = Year(19, n_missing_digits=2)  # 1900s
        assert century.start == datetime.datetime(1900, 1, 1)
        assert century.end == datetime.datetime(2000, 1, 1)


class TestUnit:
    """Tests for the Unit enum."""

    def test_unit_truncate_day(self):
        """Test truncating datetime to day boundary."""
        dt = datetime.datetime(2024, 3, 15, 14, 30, 45)
        truncated = DAY.truncate(dt)
        assert truncated == datetime.datetime(2024, 3, 15, 0, 0, 0)

    def test_unit_truncate_month(self):
        """Test truncating datetime to month boundary."""
        dt = datetime.datetime(2024, 3, 15, 14, 30, 45)
        truncated = MONTH.truncate(dt)
        assert truncated == datetime.datetime(2024, 3, 1, 0, 0, 0)

    def test_unit_truncate_year(self):
        """Test truncating datetime to year boundary."""
        dt = datetime.datetime(2024, 3, 15, 14, 30, 45)
        truncated = YEAR.truncate(dt)
        assert truncated == datetime.datetime(2024, 1, 1, 0, 0, 0)

    def test_unit_relativedelta(self):
        """Test creating relativedelta from units."""
        delta_months = MONTH.relativedelta(3)
        start = datetime.datetime(2024, 1, 1)
        end = start + delta_months
        assert end == datetime.datetime(2024, 4, 1)

        delta_years = YEAR.relativedelta(2)
        end = start + delta_years
        assert end == datetime.datetime(2026, 1, 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
