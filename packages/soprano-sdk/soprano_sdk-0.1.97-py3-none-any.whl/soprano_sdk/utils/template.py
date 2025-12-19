from typing import Any
from jinja2 import Template, TemplateError, UndefinedError
import ast


def get_nested_value(data: Any, path: str) -> Any:
    if not path:
        return data

    if not path.strip().startswith('{{'):
        template_str = f'{{{{ {path} }}}}'
    else:
        template_str = path

    try:
        template = Template(template_str)
        result = template.render(result=data)
        
        if not result or result == '':
            return None
            
        try:
            return ast.literal_eval(result)
        except (ValueError, SyntaxError):
            return result
    except (TemplateError, UndefinedError):
        return None