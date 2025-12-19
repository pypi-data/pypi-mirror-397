"""
Timenorm-Py: Python-native temporal expression parser and normalizer.

This library finds and normalizes temporal expressions in natural language text.
"""

from timenorm.types import (
    # Core types
    Interval,
    Period,
    PeriodSum,
    Repeating,
    Unit,
    Shift,
    
    # Specialized intervals
    Year,
    YearSuffix,
    
    # Operators
    Last,
    Next,
    Before,
    After,
    This,
    Nth,
    Between,
    Intersection,
    
    # Multiple interval operators
    Intervals,
    LastN,
    NextN,
    NthN,
    These,
    
    # Shift combinations
    EveryNth,
    ShiftUnion,
    RepeatingIntersection,
    
    # Predefined repeating intervals
    Spring,
    Summer,
    Fall,
    Winter,
    Weekend,
    Morning,
    Noon,
    Afternoon,
    Day,
    Evening,
    Night,
    Midnight,
    
    # Unit enum values
    MICROSECOND,
    MILLISECOND,
    SECOND,
    MINUTE,
    HOUR,
    DAY,
    WEEK,
    MONTH,
    QUARTER_YEAR,
    YEAR,
    DECADE,
    QUARTER_CENTURY,
    CENTURY,
    
    # Exception
    AnaforaXMLParsingError,
    
    # XML parsing
    from_xml,
)

# Import main parser API
from timenorm.parser import TemporalParser

__version__ = "0.1.0"

__all__ = [
    # Core types
    "Interval",
    "Period",
    "PeriodSum",
    "Repeating",
    "Unit",
    "Shift",
    # Specialized intervals
    "Year",
    "YearSuffix",
    # Operators
    "Last",
    "Next",
    "Before",
    "After",
    "This",
    "Nth",
    "Between",
    "Intersection",
    # Multiple interval operators
    "Intervals",
    "LastN",
    "NextN",
    "NthN",
    "These",
    # Shift combinations
    "EveryNth",
    "ShiftUnion",
    "RepeatingIntersection",
    # Predefined repeating intervals
    "Spring",
    "Summer",
    "Fall",
    "Winter",
    "Weekend",
    "Morning",
    "Noon",
    "Afternoon",
    "Day",
    "Evening",
    "Night",
    "Midnight",
    # Units
    "MICROSECOND",
    "MILLISECOND",
    "SECOND",
    "MINUTE",
    "HOUR",
    "DAY",
    "WEEK",
    "MONTH",
    "QUARTER_YEAR",
    "YEAR",
    "DECADE",
    "QUARTER_CENTURY",
    "CENTURY",
    # Exception
    "AnaforaXMLParsingError",
    # XML parsing
    "from_xml",
    # Main API
    "TemporalParser",
]

# Import neural parser after __all__ is defined (may fail if TensorFlow not available)
try:
    from timenorm.scate.neural_parser import TemporalNeuralParser
    __all__.append("TemporalNeuralParser")
except ImportError:
    TemporalNeuralParser = None
