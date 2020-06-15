## 
# database.py
#
# Define the Django middlewear that will manage the database
##
import psycopg2

class DatabaseMiddlewear:
    default = "host=masimdb.vmhost.psu.edu dbname=masim user=sim password=sim"
    databases = None

    # Prepare the middlewear
    def __init__(self, get_response):
        self.get_response = get_response

        self.databases = self.getDatabases()
        # Load the databases if not set
        if self.databases is None:
            self.databases = self.getDatabases()


    # Get and return the response
    def __call__(self, request):    
        # Execute before view functions
        # Set the default database if not already set (i.e. restart the server)
        # How does request.session['database'] change?
        if not 'database' in request.session:
            request.session['database'] = 1

        # Inject the database information
        self.injectDatabase(request)

        # Render the view
        response = self.get_response(request)
        return response


    def injectDatabase(self, request):
        # Note the ID (get the database id)
        database = request.session['database']
        # Raise an error if not found
        if database not in self.databases:
            raise Exception("Database {} not found in registry".format(database))

        # Inject the database information
        request.session['dbconnection'] = self.databases[database]['Connection']
        request.session['dbname'] = self.databases[database]['Name']
        request.session['databases'] = self.databases
        

    # Get the list of databases and convert them to a dictionary
    def getDatabases(self):
        SQL = "SELECT id, name, connection FROM app.database ORDER BY name"

        connection = psycopg2.connect(self.default)
        cursor = connection.cursor()
        cursor.execute(SQL)

        result = {}
        for row in cursor.fetchall():
            id = int(row[0])
            result[id] = {}
            result[id]['Name'] = row[1]
            result[id]['Connection'] = row[2]

        cursor.close()
        connection.close()

        return result
