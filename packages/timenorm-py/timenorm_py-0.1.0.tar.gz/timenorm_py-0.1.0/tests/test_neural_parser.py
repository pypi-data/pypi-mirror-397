"""
Tests for the neural parser module (basic structure tests).
"""
import datetime
import pytest
import xml.etree.ElementTree as ET

from timenorm import Interval, from_xml
from timenorm.scate.neural_parser import TemporalNeuralParser


def test_neural_parser_init():
    """Test that the neural parser can be initialized."""
    parser = TemporalNeuralParser()
    assert parser is not None


def test_neural_parser_context_manager():
    """Test that the neural parser works as a context manager."""
    with TemporalNeuralParser() as parser:
        assert parser is not None


def test_from_xml_basic():
    """Test parsing from Anafora XML format."""
    # Create a simple XML with a Year entity
    xml_str = """
    <data>
        <annotations>
            <entity>
                <id>1@id</id>
                <span>0,4</span>
                <type>Year</type>
                <properties>
                    <Value>2024</Value>
                </properties>
            </entity>
        </annotations>
    </data>
    """
    
    elem = ET.fromstring(xml_str)
    results = from_xml(elem)
    
    assert len(results) == 1
    # Should be a Year interval
    assert hasattr(results[0], 'start')
    assert hasattr(results[0], 'end')


def test_from_xml_with_period():
    """Test parsing Period from XML."""
    xml_str = """
    <data>
        <annotations>
            <entity>
                <id>1@id</id>
                <span>0,7</span>
                <type>Period</type>
                <properties>
                    <Type>Months</Type>
                    <Number>2@id</Number>
                </properties>
            </entity>
            <entity>
                <id>2@id</id>
                <span>0,3</span>
                <type>Number</type>
                <properties>
                    <Value>3</Value>
                </properties>
            </entity>
        </annotations>
    </data>
    """
    
    elem = ET.fromstring(xml_str)
    results = from_xml(elem)
    
    # Should have one Period (Number is consumed)
    assert len(results) == 1


def test_from_xml_with_last_operator():
    """Test parsing Last operator from XML."""
    xml_str = """
    <data>
        <annotations>
            <entity>
                <id>1@id</id>
                <span>0,9</span>
                <type>Last</type>
                <properties>
                    <Interval-Type>DocTime</Interval-Type>
                    <Period>2@id</Period>
                    <Semantics>Interval-Not-Included</Semantics>
                </properties>
            </entity>
            <entity>
                <id>2@id</id>
                <span>5,9</span>
                <type>Period</type>
                <properties>
                    <Type>Weeks</Type>
                    <Number>3@id</Number>
                </properties>
            </entity>
            <entity>
                <id>3@id</id>
                <span>5,6</span>
                <type>Number</type>
                <properties>
                    <Value>1</Value>
                </properties>
            </entity>
        </annotations>
    </data>
    """
    
    elem = ET.fromstring(xml_str)
    anchor = Interval.of(2024, 11, 15)
    results = from_xml(elem, known_intervals={(None, None): anchor})
    
    # Should have one Last operator result
    assert len(results) == 1
    # It should have start and end
    last_week = results[0]
    assert last_week.start is not None or last_week.end is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
