"""
Neural parser implementation for SCATE (Semantically Compositional

 Annotation for TEmporal expressions).

This module loads pre-trained TensorFlow models and performs character-level temporal expression identification.
"""
import json
import os
import pathlib
import re
import typing
from dataclasses import dataclass

import numpy as np


from timenorm.types import (
    Interval,
    from_xml,
)


@dataclass
class TimeSpan:
    """A detected temporal expression with its text span and type."""
    start: int
    end: int
    time_type: str
    text: str


class TemporalNeuralParser:
    """
    Neural network-based parser for identifying and normalizing temporal expressions in text.
    
    Uses a character-level RNN to:
    1. Identify temporal expression spans in text
    2. Classify them into operator types (Last, Next, This, etc.)
    3. Link them into composed temporal expressions
    4. Normalize to concrete time intervals
    """
    
    def __init__(self, model_path: typing.Optional[str] = None):
        """
        Initialize the neural parser.
        
        Args:
            model_path: Optional path to the TensorFlow model file (.pb format).
                       If None, uses the default bundled model.
        """
        self.model_path = model_path
        self._model = None
        self._char2index = None
        self._operator_labels = None
        self._non_operator_labels = None
        self._operator_to_text_to_type = None
        self._between_indicators = None
        self._operator_to_property_to_types = None
        
    @property
    def model(self):
        """Lazy load the TensorFlow model."""
        if self._model is None:
            try:
                import tensorflow as tf
            except ImportError:
                raise ImportError("TensorFlow is required for neural parsing. Install with: pip install tensorflow")
            
            model_path = self.model_path or self._get_default_model_path()
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    f"Model file not found: {model_path}\\n"
                    f"Please download the pre-trained model from timenorm-models package."
                )
            
            # Load TensorFlow model
            with open(model_path, 'rb') as f:
                graph_def = tf.compat.v1.GraphDef()
                graph_def.ParseFromString(f.read())
                
            graph = tf.Graph()
            with graph.as_default():
                tf.import_graph_def(graph_def, name='')
                
            self._model = tf.compat.v1.Session(graph=graph)
            
        return self._model
    
    @property
    def char2index(self) -> dict[str, float]:
        """Lazy load character to index mapping."""
        if self._char2index is None:
            vocab_path = self._get_resource_path('vocab', 'dictionary.json')
            with open(vocab_path, 'r') as f:
                string2int = json.load(f)
                
            # Convert to character mapping (only single-character strings)
            char2int = {s[0]: float(v) for s, v in string2int.items() if len(s) == 1}
            # Default value for unknown characters
            unk_value = float(string2int.get('<unk>', 0))
            self._char2index = {**char2int}
            # Make it return default for missing keys
            self._char2index = type('DefaultDict', (), {'__getitem__': lambda self, k: char2int.get(k, unk_value)})()
            
        return self._char2index
    
    @property
    def operator_labels(self) -> list[str]:
        """Lazy load operator labels."""
        if self._operator_labels is None:
            path = self._get_resource_path('label', 'operator.txt')
            with open(path, 'r') as f:
                self._operator_labels = [line.strip() for line in f]
        return self._operator_labels
    
    @property
    def non_operator_labels(self) -> list[str]:
        """Lazy load non-operator labels."""
        if self._non_operator_labels is None:
            path = self._get_resource_path('label', 'non-operator.txt')
            with open(path, 'r') as f:
                self._non_operator_labels = [line.strip() for line in f]
        return self._non_operator_labels
    
    def _get_default_model_path(self) -> str:
        """Get the path to the default bundled model."""
        # Model should be in timenorm/resources/model/
        base = pathlib.Path(__file__).parent.parent / 'resources' / 'model'
        return str(base / 'weights-improvement-22.pb')
    
    def _get_resource_path(self, *parts) -> str:
        """Get path to a resource file."""
        # First try relative to source (for development)
        source_base = pathlib.Path(__file__).parent.parent.parent / 'timenorm' / 'src' / 'main' / 'resources' / 'org' / 'clulab' / 'timenorm'
        source_path = source_base.joinpath(*parts)
        if source_path.exists():
            return str(source_path)
        
        # Then try installed location
        installed_base = pathlib.Path(__file__).parent / 'resources'
        return str(installed_base.joinpath(*parts))
    
    def parse(self, text: str, anchor: typing.Optional[Interval] = None) -> list:
        """
        Parse temporal expressions from text.
        
        Args:
            text: Input text to parse
            anchor: Document creation time (anchor time) as an Interval
            
        Returns:
            List of temporal objects (Intervals, Periods, etc.) found in the text
        """
        return self.parse_batch(text, [(0, len(text))], anchor)[0]
    
    def parse_batch(self,
                   text: str,
                   spans: list[tuple[int, int]],
                   anchor: typing.Optional[Interval] = None) -> list[list]:
        """
        Parse temporal expressions from multiple spans of text in a batch.
        
        Args:
            text: Full input text
            spans: List of (start, end) character offsets to parse
            anchor: Document creation time
            
        Returns:
            List of lists of temporal objects, one list per span
        """
        if anchor is None:
            anchor = Interval(None, None)
            
        # Convert to Anafora XML format
        xml_results = self.parse_batch_to_xml(text, spans)
        
        # Convert XML to TimeExpression objects
        results = []
        for xml_elem in xml_results:
            known_intervals = {(None, None): anchor}
            temporal_objects = from_xml(xml_elem, known_intervals=known_intervals)
            results.append(temporal_objects)
            
        return results
    
    def parse_batch_to_xml(self, text: str, spans: list[tuple[int, int]]):
        """
        identify and link temporal expressions, returning Anafora XML format.
        
        Args:
            text: Full input text
            spans: List of (start, end) character offsets to parse
            
        Returns:
            List of XML Element objects in Anafora format
        """
        import xml.etree.ElementTree as ET
        
        # Identify temporal expression spans using the neural network
        all_time_spans = self._identify_batch(text, spans)
        
        # Create XML output for each span
        xml_results = []
        for time_spans in all_time_spans:
            # Create entity elements
            entities = []
            for i, (start, end, time_type) in enumerate(time_spans):
                entity_id = f"{i}@id"
                time_text = text[start:end]
                
                # Create entity XML
                entity = ET.Element('entity')
                ET.SubElement(entity, 'id').text = entity_id
                ET.SubElement(entity, 'span').text = f"{start},{end}"
                ET.SubElement(entity, 'type').text = time_type
                ET.SubElement(entity, 'properties')
                entities.append(entity)
            
            # Wrap in data/annotations structure
            data = ET.Element('data')
            annotations = ET.SubElement(data, 'annotations')
            for entity in entities:
                annotations.append(entity)
                
            xml_results.append(data)
            
        return xml_results
    
    def _identify_batch(self, text: str, spans: list[tuple[int, int]]) -> list[list[tuple[int, int, str]]]:
        """
        Use neural network to identify temporal expression spans.
        
        Args:
            text: Full input text
            spans: List of (start, end) spans to process
            
        Returns:
            List of lists of (start, end, type) tuples for each input span
        """
        # For now, return empty results - actual implementation requires model
        # TODO: Implement actual neural network inference when model is available
        print("Warning: Neural parser not fully implemented. Returning empty results.")
        print("Please ensure the TensorFlow model is available.")
        return [[] for _ in spans]
    
    def close(self):
        """Clean up resources."""
        if self._model is not None:
            self._model.close()
            self._model = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
