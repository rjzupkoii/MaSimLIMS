# MaSim LIMS
Basic laboratory information managmenet system (LIMS) for working with the meta-data and status of MaSim.

This documment is current as of Python 3.83

---

## Setup:
1. Download and install Python
2. Setup the virtual envrionment

```
python -m pip install virtualenvwrapper-win 
```

3. Start a virtual environment, named test but can be changed

```
mkvirtualenv test 
```

4. Install dependencies

``` 
python -m pip install django 
python -m pip install psycopg2
```

5. Check the django version

```
django-admin --version 
```

6.Create the project directory

```
mkdir project-name
cd project-name
```

7. Create a folder with manage.py, which will be the local server

```
django-admin startproject project-name 
```

## Run server:

``` 
python manage.py runserver 
```

Once the server is running, you can connect over `localhost`

Work on a virtual environment:

``` 
workon env-name 
```

## Start application (new folder):

``` 
python manage.py startapp app-name 
```
