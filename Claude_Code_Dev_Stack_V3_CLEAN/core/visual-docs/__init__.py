"""
Visual Documentation Pipeline
Creates comprehensive visual documentation from code and patterns
"""

from .pipeline.visual_docs_pipeline import VisualDocsPipeline, DocumentationConfig, create_default_config

__version__ = "1.0.0"
__author__ = "Claude Code Dev Stack"
__description__ = "Comprehensive visual documentation generator with CodeBoarding integration"

__all__ = [
    'VisualDocsPipeline',
    'DocumentationConfig', 
    'create_default_config'
]