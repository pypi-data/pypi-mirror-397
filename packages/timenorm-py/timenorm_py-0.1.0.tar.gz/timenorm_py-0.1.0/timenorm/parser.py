"""
Unified parser API for timenorm-py.

This module provides a simple, high-level interface for parsing temporal expressions.
"""
import datetime
import typing
from pathlib import Path

from timenorm.types import Interval, from_xml
from timenorm.scate.neural_parser import TemporalNeuralParser


class TemporalParser:
    """
    High-level unified interface for parsing temporal expressions from text.
    
    This class provides a simple API that automatically handles:
    - Neural network-based temporal expression identification (when model available)
    - Compositional temporal expression normalization
    - Anchor time management
    - Batch processing
    
    Example:
        >>> from timenorm import TemporalParser, Interval
        >>> parser = TemporalParser()
        >>> anchor = Interval.of(2024, 11, 19)
        >>> results = parser.parse("I saw her last week", anchor=anchor)
        >>> for expr in results:
        ...     print(f"{expr}")
    """
    
    def __init__(self, 
                 model_path: typing.Optional[str] = None,
                 method: str = 'neural'):
        """
        Initialize the temporal parser.
        
        Args:
            model_path: Optional path to TensorFlow model file. If None, uses default.
            method: Parsing method - 'neural' (default) or 'xml' (for pre-annotated XML)
        """
        self.method = method
        self._neural_parser = None
        self.model_path = model_path
        
    @property
    def neural_parser(self) -> TemporalNeuralParser:
        """Lazy-load the neural parser."""
        if self._neural_parser is None:
            self._neural_parser = TemporalNeuralParser(model_path=self.model_path)
        return self._neural_parser
    
    def parse(self, 
              text: str, 
              anchor: typing.Optional[Interval] = None) -> list:
        """
        Parse temporal expressions from text.
        
        Args:
            text: Input text containing temporal expressions
            anchor: Document creation time (anchor time). If None, uses current time.
            
        Returns:
            List of temporal expression objects (Intervals, Periods, operators, etc.)
            
        Example:
            >>> parser = TemporalParser()
            >>> results = parser.parse("I'll see you next Tuesday", 
            ...                        anchor=Interval.of(2024, 11, 19))
        """
        if anchor is None:
            anchor = self._create_default_anchor()
            
        if self.method == 'neural':
            return self.neural_parser.parse(text, anchor=anchor)
        else:
            raise ValueError(f"Unknown parsing method: {self.method}")
    
    def parse_batch(self,
                   text: str,
                   spans: typing.Optional[list[tuple[int, int]]] = None,
                   anchor: typing.Optional[Interval] = None) -> list[list]:
        """
        Parse temporal expressions from multiple text spans in a batch.
        
        Args:
            text: Full input text
            spans: List of (start, end) character offset pairs to parse.
                   If None, parses the entire text.
            anchor: Document creation time. If None, uses current time.
            
        Returns:
            List of lists of temporal expressions, one list per span.
            
        Example:
            >>> parser = TemporalParser()
            >>> text = "Monday meeting. Tuesday lunch."
            >>> spans = [(0, 15), (16, 30)]
            >>> results = parser.parse_batch(text, spans, 
            ...                             anchor=Interval.of(2024, 11, 19))
        """
        if anchor is None:
            anchor = self._create_default_anchor()
            
        if spans is None:
            spans = [(0, len(text))]
            
        if self.method == 'neural':
            return self.neural_parser.parse_batch(text, spans, anchor=anchor)
        else:
            raise ValueError(f"Unknown parsing method: {self.method}")
    
    def parse_file(self,
                   file_path: typing.Union[str, Path],
                   anchor: typing.Optional[Interval] = None) -> list:
        """
        Parse temporal expressions from a text file.
        
        Args:
            file_path: Path to text file to parse
            anchor: Document creation time. If None, uses current time.
            
        Returns:
            List of temporal expressions found in the file.
            
        Example:
            >>> parser = TemporalParser()
            >>> results = parser.parse_file("document.txt", 
            ...                            anchor=Interval.of(2024, 11, 19))
        """
        file_path = Path(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return self.parse(text, anchor=anchor)
    
    def parse_xml(self,
                  xml_path: typing.Union[str, Path],
                  anchor: typing.Optional[Interval] = None) -> list:
        """
        Parse temporal expressions from Anafora XML file.
        
        Args:
            xml_path: Path to Anafora XML file
            anchor: Document creation time for resolving relative expressions.
                    If None, uses current time.
            
        Returns:
            List of temporal expressions from the XML annotations.
            
        Example:
            >>> parser = TemporalParser()
            >>> results = parser.parse_xml("annotations.xml",
            ...                           anchor=Interval.of(2024, 11, 19))
        """
        import xml.etree.ElementTree as ET
        
        if anchor is None:
            anchor = self._create_default_anchor()
            
        xml_path = Path(xml_path)
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        known_intervals = {(None, None): anchor}
        return from_xml(root, known_intervals=known_intervals)
    
    def _create_default_anchor(self) -> Interval:
        """Create default anchor time (current date)."""
        today = datetime.date.today()
        return Interval.of(today.year, today.month, today.day)
    
    def close(self):
        """Clean up resources."""
        if self._neural_parser is not None:
            self._neural_parser.close()
            self._neural_parser = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
    
    def __repr__(self):
        return f"TemporalParser(method='{self.method}')"
