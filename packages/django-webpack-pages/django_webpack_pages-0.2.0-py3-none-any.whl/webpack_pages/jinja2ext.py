"""The Jinja2 extension that provides the templatetags."""

import jinja2
import jinja2.ext
from jinja2.utils import pass_context

from .templatetags import asset_url, inline_entrypoint, register_entrypoint, render_css, render_js


class WebpackExtension(jinja2.ext.Extension):
    """The Jinja2 extension that provides the templatetags."""

    def __init__(self, environment: jinja2.Environment) -> None:
        super().__init__(environment)
        environment.globals.update(
            {
                "register_entrypoint": pass_context(register_entrypoint),
                "render_css": pass_context(render_css),
                "render_js": pass_context(render_js),
                "inline_entrypoint": inline_entrypoint,
                "asset": pass_context(asset_url),
            },
        )
