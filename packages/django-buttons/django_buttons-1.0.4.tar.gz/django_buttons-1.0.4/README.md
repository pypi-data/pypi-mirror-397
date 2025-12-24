# django-buttons

This application provides some simple template tags to insert buttons into templates.

## Installation

Install application with pypi:

```sh
$ pip install django-buttons[fa5]  # Installs django-fontawesome5
$ pip install django-buttons[fa6]  # Installs django-fontawesome6
```

Add application to your INSTALLED_APPS:

```python
INSTALLED_APPS = [
    ...
    'buttons',
    ...
]

BUTTONS_FONTAWESOME_VERSION = 4  # Use 5 to use fontawesome-5 as icon library
```

## Use buttons in your templates

```html
 {% load buttons_tags %}
...
{% btn_home %}
```

Buttons can have some parameters :

+ **url**: target url
+ **title**: displayed text
+ **icon**: fa aware name, ie. 'home' for
  [fa-home](http://fontawesome.io/icon/home/)
+ **icon_position**: Position of the icon, 'right', 'left' or 'none'
  (no icon displayed) ...

**Enjoy !**
