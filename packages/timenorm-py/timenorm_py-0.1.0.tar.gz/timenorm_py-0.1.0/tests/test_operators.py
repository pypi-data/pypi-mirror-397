"""
Unit tests for temporal operators (Last, Next, Before, After, This, Between, etc.).
"""
import datetime
import pytest
from timenorm import (
    Interval,
    Period,
    Repeating,
    Last,
    Next,
    Before,
    After,
    This,
    Between,
    Nth,
    DAY,
    WEEK,
    MONTH,
    YEAR,
)


class TestLast:
    """Tests for the Last operator."""

    def test_last_period(self):
        """Test 'last 7 days' - period ending at anchor."""
        anchor = Interval.of(2024, 11, 15)
        last_week = Last(anchor, Period(DAY, 7))

        assert last_week.start == datetime.datetime(2024, 11, 8)
        assert last_week.end == datetime.datetime(2024, 11, 15)

    def test_last_repeating(self):
        """Test 'last Tuesday' - last Tuesday before anchor."""
        anchor = Interval.of(2024, 11, 15)  # Friday
        # Tuesday = 1 in dateutil (Monday=0)
        last_tuesday = Last(anchor, Repeating(DAY, WEEK, value=1))

        assert last_tuesday.start == datetime.datetime(2024, 11, 12)
        assert last_tuesday.end == datetime.datetime(2024, 11, 13)

    def test_last_month(self):
        """Test 'last October' - October before current time."""
        anchor = Interval.of(2024, 11, 15)
        last_october = Last(anchor, Repeating(MONTH, YEAR, value=10))

        assert last_october.start == datetime.datetime(2024, 10, 1)
        assert last_october.end == datetime.datetime(2024, 11, 1)


class TestNext:
    """Tests for the Next operator."""

    def test_next_period(self):
        """Test 'next 3 weeks' - period starting at anchor end."""
        anchor = Interval.of(2024, 11, 15)
        next_weeks = Next(anchor, Period(WEEK, 3))

        assert next_weeks.start == datetime.datetime(2024, 11, 16)
        assert next_weeks.end == datetime.datetime(2024, 12, 7)

    def test_next_repeating(self):
        """Test 'next Tuesday' - first Tuesday after anchor."""
        anchor = Interval.of(2024, 11, 15)  # Friday
        next_tuesday = Next(anchor, Repeating(DAY, WEEK, value=1))

        assert next_tuesday.start == datetime.datetime(2024, 11, 19)
        assert next_tuesday.end == datetime.datetime(2024, 11, 20)

    def test_next_month(self):
        """Test 'next March' - March after current time."""
        anchor = Interval.of(2024, 11, 15)
        next_march = Next(anchor, Repeating(MONTH, YEAR, value=3))

        assert next_march.start == datetime.datetime(2025, 3, 1)
        assert next_march.end == datetime.datetime(2025, 4, 1)


class TestBefore:
    """Tests for the Before operator."""

    def test_before_period(self):
        """Test '3 days before Tuesday' - shift back by period."""
        tuesday = Interval.of(2024, 11, 19)
        three_days_before = Before(tuesday, Period(DAY, 3))

        # Should be shifted back 3 days, maintaining 1-day width
        assert three_days_before.start == datetime.datetime(2024, 11, 16)
        assert three_days_before.end == datetime.datetime(2024, 11, 17)

    def test_before_repeating(self):
        """Test '2 Mondays before Thanksgiving'."""
        thanksgiving = Interval.of(2024, 11, 28)  # Thursday
        monday = Repeating(DAY, WEEK, value=0)  # Monday = 0
        two_mondays_before = Before(thanksgiving, monday, n=2)

        # 2 Mondays before Nov 28 should be Nov 18
        assert two_mondays_before.start == datetime.datetime(2024, 11, 18)
        assert two_mondays_before.end == datetime.datetime(2024, 11, 19)


class TestAfter:
    """Tests for the After operator."""

    def test_after_period(self):
        """Test '2 weeks after Christmas' - shift forward by period."""
        christmas = Interval.of(2024, 12, 25)
        two_weeks_after = After(christmas, Period(WEEK, 2))

        assert two_weeks_after.start == datetime.datetime(2025, 1, 8)
        assert two_weeks_after.end == datetime.datetime(2025, 1, 9)

    def test_after_repeating(self):
        """Test 'Friday after Thanksgiving'."""
        thanksgiving = Interval.of(2024, 11, 28)  # Thursday
        friday = Repeating(DAY, WEEK, value=4)  # Friday = 4
        friday_after = After(thanksgiving, friday)

        assert friday_after.start == datetime.datetime(2024, 11, 29)
        assert friday_after.end == datetime.datetime(2024, 11, 30)


class TestThis:
    """Tests for the This operator."""

    def test_this_period(self):
        """Test 'these six days' - period centered on anchor."""
        anchor = Interval.of(2024, 11, 15)
        these_six_days = This(anchor, Period(DAY, 6))

        # Should be centered around Nov 15 (12:00 noon)
        # Half of 6 days = 3 days, so goes from noon Nov 12 to noon Nov 18
        assert these_six_days.start == datetime.datetime(2024, 11, 12, 12, 0)
        assert these_six_days.end == datetime.datetime(2024, 11, 18, 12, 0)

    def test_this_repeating_month(self):
        """Test 'this January' spoken in November - January of this year."""
        anchor = Interval.of(2024, 11, 10)
        this_january = This(anchor, Repeating(MONTH, YEAR, value=1))

        assert this_january.start == datetime.datetime(2024, 1, 1)
        assert this_january.end == datetime.datetime(2024, 2, 1)


class TestBetween:
    """Tests for the Between operator."""

    def test_between_basic(self):
        """Test 'between Monday and Friday'."""
        monday = Interval.of(2024, 11, 18)
        friday = Interval.of(2024, 11, 22)
        between = Between(monday, friday)

        # Default: end of first to start of second
        assert between.start == datetime.datetime(2024, 11, 19)
        assert between.end == datetime.datetime(2024, 11, 22)

    def test_between_inclusive(self):
        """Test 'from Monday through Friday' (both included)."""
        monday = Interval.of(2024, 11, 18)
        friday = Interval.of(2024, 11, 22)
        between = Between(monday, friday, start_included=True, end_included=True)

        assert between.start == datetime.datetime(2024, 11, 18)
        assert between.end == datetime.datetime(2024, 11, 23)

    def test_since(self):
        """Test 'since 1994' (start included, end at document time)."""
        from timenorm import Year
        
        year_1994 = Year(1994)
        doc_time = Interval.of(2007, 1, 9)
        since = Between(year_1994, doc_time, start_included=False, end_included=False)

        assert since.start == datetime.datetime(1995, 1, 1)
        assert since.end == datetime.datetime(2007, 1, 9)


class TestNth:
    """Tests for the Nth operator."""

    def test_nth_day_of_month(self):
        """Test '15th day of November 2024'."""
        november = Interval.of(2024, 11)
        day = Repeating(DAY)  # Generic day repeating
        fifteenth = Nth(november, day, 15)  # 15th day within November

        assert fifteenth.start == datetime.datetime(2024, 11, 15)
        assert fifteenth.end == datetime.datetime(2024, 11, 16)

    def test_third_tuesday(self):
        """Test '3rd Tuesday of November 2024'."""
        november = Interval.of(2024, 11)
        tuesday = Repeating(DAY, WEEK, value=1)  # Tuesday = 1
        third_tuesday = Nth(november, tuesday, 3)  # interval, shift, index

        # 3rd Tuesday of November 2024 is Nov 19
        assert third_tuesday.start == datetime.datetime(2024, 11, 19)
        assert third_tuesday.end == datetime.datetime(2024, 11, 20)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
