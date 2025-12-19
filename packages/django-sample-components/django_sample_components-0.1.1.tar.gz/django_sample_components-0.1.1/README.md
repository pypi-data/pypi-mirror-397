
# django-sample-components 🚀

[![PyPI](https://img.shields.io/pypi/v/django-sample-components.svg)](https://pypi.org/project/django-sample-components/)


> This project is a test for creating a Django library. 🧩


## Installation 📦

You can install the library using pip or poetry:

```bash
pip install django-sample-components
```

or

```bash
poetry add django-sample-components
```


## Configuration ⚙️

Add `django_sample_components` to the `INSTALLED_APPS` list in your `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps ...
    'django_sample_components',
]
```

### Usage in Templates 📝

Now you can use `sample_tags` in your templates as follows (*templates/explample.html*):

```html
{% load sample_tags %}

<p>{% greeting "Bob" %}</p>
<p>{% shout %}Let's go!{% endshout %}</p>
```



## Migrations 🗄️

After installing and configuring, run the following commands:

```bash
python manage.py makemigrations
python manage.py migrate
```


🎉 Done! Your Django library is installed and ready to use.


## Running locally as a developer 🖥️

To run the Django project locally during development, follow the steps below:

```bash
git clone https://github.com/GustavoRizzo/django-sample-components.git
cd django-sample-components
poetry install
cd demo_project
pip install -e ..
poetry run ./manage.py runserver
```

### Tests 🧪
To run the tests, use the command below inside the `demo_project` directory:

```bash
poetry run ./manage.py test
```


## Updating and publishing the library 🚢

To update the version, build, and publish your library, use the commands below:

```bash
poetry version patch  # to bump the version (e.g.: 0.1.0 → 0.1.1)
poetry build
tar -tzf dist/*.tar.gz | head -20  # to see the files inside the package
poetry publish
```
