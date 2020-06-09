# MaSim LIMS
Add some insertion and delete features to our Web GUI

Setup:
1. Download and install Python
2. Setup the virtual envrionment

``` pip install virtualenvwrapper-win ```

3. Start a virtual environment, named test but can be changed

``` mkvirtualenv test ```

4. Install dependencies

``` 
pip install django 
pip install psycopg2
```

5. Check the django version

``` django-admin --version ```

6.Create the project directory

```
mkdir project-name
cd project-name
```

7. Create a folder with manage.py, which will be the local server

``` django-admin startproject project-name ```

Run server:

``` python manage.py runserver ```

Once the server is running, you can connect over `localhost`

Work on a virtual environment:

``` workon env-name ```

Start application (new folder):

``` python manage.py startapp app-name ```
