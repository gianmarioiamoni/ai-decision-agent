# app/report/template_loader.py
#
# Template loader for HTML report generation.
#
# Responsibilities:
# - Load HTML templates from disk
# - Render templates with provided data
# - Cache templates for performance
#

import os
from string import Template
from typing import Dict, Any


class TemplateLoader:
    #
    # Loads and renders HTML templates using Python's string.Template.
    #
    # Templates are stored in app/report/templates/ directory.
    # Uses simple $variable substitution (no complex logic needed).
    #
    
    def __init__(self, templates_dir: str = None):
        #
        # Initialize template loader.
        #
        # Args:
        #     templates_dir: Path to templates directory (default: auto-detect)
        #
        if templates_dir is None:
            # Auto-detect: same directory as this file + /templates
            current_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(current_dir, "templates")
        
        self.templates_dir = templates_dir
        self._cache = {}  # Cache loaded templates
    
    def load_template(self, template_name: str) -> Template:
        #
        # Load a template from disk (with caching).
        #
        # Args:
        #     template_name: Name of template file (e.g., "report_full.html")
        #
        # Returns:
        #     string.Template object ready for substitution
        #
        # Raises:
        #     FileNotFoundError: If template file doesn't exist
        #
        
        # Check cache first
        if template_name in self._cache:
            return self._cache[template_name]
        
        # Load from disk
        template_path = os.path.join(self.templates_dir, template_name)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Create Template and cache it
        template = Template(template_content)
        self._cache[template_name] = template
        
        return template
    
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        #
        # Render a template with provided context data.
        #
        # Args:
        #     template_name: Name of template file
        #     context: Dictionary of variables to substitute in template
        #
        # Returns:
        #     Rendered HTML string
        #
        template = self.load_template(template_name)
        return template.safe_substitute(context)
    
    def clear_cache(self):
        #
        # Clear template cache (useful for development/testing).
        #
        self._cache.clear()


# Singleton instance for easy import
_loader = None

def get_template_loader() -> TemplateLoader:
    #
    # Get singleton TemplateLoader instance.
    #
    # Returns:
    #     Shared TemplateLoader instance
    #
    global _loader
    if _loader is None:
        _loader = TemplateLoader()
    return _loader

