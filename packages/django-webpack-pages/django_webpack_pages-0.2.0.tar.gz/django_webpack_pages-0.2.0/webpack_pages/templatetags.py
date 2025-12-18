"""Jinja2 templatetags of django-webpack-pages."""

import functools
import os
import typing

import django.template
import jinja2.runtime
from django.conf import settings
from django.contrib.staticfiles import finders
from django.utils import translation
from django.utils.safestring import SafeString, mark_safe
from webpack_loader.utils import get_files

from .pageassetfinder import PageAssetFinder
from .utils import conditional_decorator, is_first_visit

register = django.template.Library()


class SpecialContext(jinja2.runtime.Context):
    webpack_entrypoints: list[str]
    webpack_pops: int
    assets_pagename: str


def get_unique_files(entrypoints: typing.Sequence, extension: str, config: str) -> list[dict]:
    """For multiple entrypoints (or bundles), scans through their files and deduplicates them."""
    if settings.WEBPACK_PAGES["STRATEGY"] == "ACCRUE":
        files = list(get_files(entrypoints[0], extension, config=config))
        for ep in entrypoints[1:]:
            files += [file for file in get_files(ep, extension, config=config) if file not in files]
        return files
    if settings.WEBPACK_PAGES["STRATEGY"] == "LAST":
        return list(get_files(entrypoints[-1], extension, config))
    raise NotImplementedError


@register.simple_tag(takes_context=True)
def register_entrypoint(context: SpecialContext, entrypoint: str, *, pop_parents: int = 0) -> None:
    """Register an entrypoint to be used later."""
    if not hasattr(context, "webpack_entrypoints"):
        context.webpack_entrypoints = []
    if not hasattr(context, "webpack_pops"):
        context.webpack_pops = 0
    if context.webpack_pops == 0:
        context.webpack_entrypoints.insert(0, entrypoint)  # fill it in reverse
    else:
        context.webpack_pops -= 1  # we've performed the pop by skipping insert()
    context.webpack_pops += pop_parents


@register.simple_tag(takes_context=True)
def render_css(context: SpecialContext, config: str = "DEFAULT") -> SafeString:
    """Render <style> and/or <link> tags, depending on the use of CRITICAL_CSS. Should be put in the <head>."""
    entrypoints = getattr(context, "webpack_entrypoints", [])
    preload_tags = []
    noscript_tags = []
    for file in get_unique_files(entrypoints, "css", config):
        preload_tags.append(
            f'<link rel="preload" href="{file["url"]}" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">',
        )
        noscript_tags.append(f'<link rel="stylesheet" href="{file["url"]}">')
    base = settings.WEBPACK_PAGES["STATICFILE_BUNDLES_BASE"].format(locale=translation.get_language())
    critical_path = finders.find(f"{base}{entrypoints[-1]}.critical.css")
    if isinstance(critical_path, list):  # should not happen as we did not pass "all" parameter
        critical_path = critical_path[0]
    if is_first_visit(context["request"]) and settings.WEBPACK_PAGES["CRITICAL_CSS_ENABLED"] and critical_path:
        with open(critical_path, encoding="utf-8") as f:
            critical_css = f.read()
        return typing.cast(
            "SafeString",
            mark_safe(
                f"<style>{critical_css}</style>\n"
                f"{''.join(preload_tags)}\n"
                f"<script>{inline_static_file(base + 'cssrelpreload.js')}</script>\n"
                f"<noscript>{''.join(noscript_tags)}</noscript>",
            ),
        )
    return typing.cast("SafeString", mark_safe("".join(noscript_tags)))


@register.simple_tag(takes_context=True)
def render_js(context: SpecialContext, config: str = "DEFAULT") -> SafeString:
    """Similar to render_css, but for JavaScript."""
    files = get_unique_files(getattr(context, "webpack_entrypoints", []), "js", config)
    return typing.cast("SafeString", mark_safe("".join(f"<script src='{file['url']}'></script>" for file in files)))


@conditional_decorator(functools.lru_cache(), condition=not settings.DEBUG)
def inline_static_file(path: str) -> SafeString:
    """Plain static file inlining utility, with caching."""
    with open(finders.find(path), encoding="utf-8") as f:  # type: ignore reportArgumentType
        return typing.cast("SafeString", mark_safe(f.read()))


@conditional_decorator(functools.lru_cache(), condition=not settings.DEBUG)
def inline_entrypoint(entrypoint: str, extension: str, config: str = "DEFAULT") -> SafeString:
    """Inlines all files of an entrypoint directly (i.e. returns a string)."""
    inlined = ""
    base = settings.WEBPACK_PAGES["STATICFILE_BUNDLES_BASE"].format(locale=translation.get_language())
    for file in get_unique_files((entrypoint,), extension, config=config):
        with open(finders.find(base + file["name"]), encoding="utf-8") as f:  # type: ignore reportArgumentType
            inlined += f.read()
    return typing.cast("SafeString", mark_safe(inlined))


@register.simple_tag(takes_context=True)
def asset_url(context: SpecialContext, path: str, *, absolute: bool = False) -> str:
    """Returns an asset URL, should be called from within a page template."""
    if absolute:
        pagename, _, path = path.partition("/")
    elif hasattr(context, "assets_pagename"):
        pagename = context.assets_pagename
    else:
        if context.name is None:
            raise ValueError
        template = context.environment.get_template(context.name)
        if template.filename is None:
            raise ValueError
        pages_location = os.path.normpath(template.filename)[: -(len(os.path.normpath(context.name)) + 1)]
        if pages_location == settings.WEBPACK_PAGES["ROOT_PAGE_DIR"]:
            app_name = "root"
        else:
            app_name = os.path.basename(os.path.dirname(pages_location))
        pagename = os.path.join(app_name, os.path.dirname(context.name)).replace(os.path.sep, ".")
        context.assets_pagename = pagename  # caching for next asset
    return PageAssetFinder.page_asset_url(pagename, path)
