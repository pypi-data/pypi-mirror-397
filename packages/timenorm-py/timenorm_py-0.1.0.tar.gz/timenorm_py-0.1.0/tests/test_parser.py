"""
Tests for the unified TemporalParser API.
"""
import datetime
import tempfile
from pathlib import Path

import pytest
from timenorm import TemporalParser, Interval


def test_temporal_parser_init():
    """Test parser initialization."""
    parser = TemporalParser()
    assert parser is not None
    assert parser.method == 'neural'


def test_temporal_parser_with_method():
    """Test parser with specific method."""
    parser = TemporalParser(method='neural')
    assert parser.method == 'neural'


def test_temporal_parser_context_manager():
    """Test parser as context manager."""
    with TemporalParser() as parser:
        assert parser is not None


def test_temporal_parser_repr():
    """Test parser string representation."""
    parser = TemporalParser()
    assert "TemporalParser" in repr(parser)
    assert "neural" in repr(parser)


def test_parse_with_anchor():
    """Test parsing with explicit anchor time."""
    parser = TemporalParser()
    anchor = Interval.of(2024, 11, 19)
    
    # Currently returns empty (no model), but shouldn't error
    results = parser.parse("I saw her last week", anchor=anchor)
    assert isinstance(results, list)


def test_parse_without_anchor():
    """Test parsing without anchor (uses current date)."""
    parser = TemporalParser()
    
    # Should use today's date as default anchor
    results = parser.parse("next Tuesday")
    assert isinstance(results, list)


def test_parse_batch():
    """Test batch parsing."""
    parser = TemporalParser()
    text = "Monday meeting. Tuesday lunch."
    spans = [(0, 15), (16, 30)]
    anchor = Interval.of(2024, 11, 19)
    
    results = parser.parse_batch(text, spans, anchor=anchor)
    assert isinstance(results, list)
    assert len(results) == 2


def test_parse_batch_full_text():
    """Test batch parsing without explicit spans."""
    parser = TemporalParser()
    text = "See you next week"
    anchor = Interval.of(2024, 11, 19)
    
    # No spans provided - should parse entire text
    results = parser.parse_batch(text, anchor=anchor)
    assert isinstance(results, list)
    assert len(results) == 1


def test_parse_file(tmp_path):
    """Test parsing from file."""
    # Create temporary file
    test_file = tmp_path / "test.txt"
    test_file.write_text("I saw her last Tuesday.")
    
    parser = TemporalParser()
    anchor = Interval.of(2024, 11, 19)
    
    results = parser.parse_file(test_file, anchor=anchor)
    assert isinstance(results, list)


def test_parse_xml(tmp_path):
    """Test parsing from XML file."""
    # Create temporary XML file
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
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
    
    xml_file = tmp_path / "test.xml"
    xml_file.write_text(xml_content)
    
    parser = TemporalParser()
    anchor = Interval.of(2024, 11, 19)
    
    results = parser.parse_xml(xml_file, anchor=anchor)
    assert isinstance(results, list)
    assert len(results) == 1  # Should have parsed the Year entity


def test_default_anchor_creation():
    """Test that default anchor uses current date."""
    parser = TemporalParser()
    anchor = parser._create_default_anchor()
    
    # Should be today's date
    today = datetime.date.today()
    assert anchor.start.year == today.year
    assert anchor.start.month == today.month
    assert anchor.start.day == today.day


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
