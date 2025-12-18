# django-webpack-pages

[![PyPI version](https://badge.fury.io/py/django-webpack-pages.svg)](https://pypi.org/project/django-webpack-pages/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Use webpack with your multi-page, multi-lingual django webapp.

This project is based on [django-webpack-loader](https://pypi.org/project/django-webpack-loader/)
which handles the connection to webpack.
Consider using [webpack-critical-pages](https://www.npmjs.com/package/webpack-critical-pages) as well
if you are interested in speedups.

Put the following in your settings file:

```python
WEBPACK_PAGES = {
    "CRITICAL_CSS_ENABLED": True,
    "ROOT_PAGE_DIR": osp.join(BASE_DIR, "pages"),
    "STATICFILE_BUNDLES_BASE": "bundles/{locale}/",  # should end in /
}

STATICFILES_FINDERS = (
    "webpack_pages.pageassetfinder.PageAssetFinder",
    # ... and more of your choosing:
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# configure the loaded page directories and add the WebpackExtension
TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "DIRS": [osp.join(BASE_DIR, "templates"), osp.join(BASE_DIR, "pages")]
        + [osp.join(BASE_DIR, app, "pages") for app in GRAZBALL_APPS]
        + [osp.join(BASE_DIR, app, "components") for app in GRAZBALL_APPS],
        "APP_DIRS": True,
        "OPTIONS": {
            # ...
            "extensions": [
                # ...
                "webpack_pages.jinja2ext.WebpackExtension",
            ],
        }
    }
]
```

Using `webpack_loader.contrib.pages` you can register entrypoints for corresponding pages in templates.

At the top of your individual page, do:

```jinja2
{% extends "layout.jinja" %}
{% do register_entrypoint("myapp/dashboard") %}
```

In the layout's (base template's) head, place the following:

```jinja2
<!DOCTYPE html>
{% do register_entrypoint("main") %}
<html lang="{{ LANGUAGE_CODE }}">
<head>
  ...
  {{ render_css() }}
</head>
<body>
  ...
  {{ render_js() }}
</body>
```

This will load the registered entrypoints in order (`main`, then `myapp/dashboard`) and automatically inject
the webpack-generated css and js. It also supports critical css injection upon first request visits.
