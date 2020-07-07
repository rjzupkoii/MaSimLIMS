## 
# database.py
#
# Define the Django middlewear that will manage the database
##
import psycopg2

class DatabaseMiddlewear:
    # default connection
    default = "host=masimdb.vmhost.psu.edu dbname=masim user=sim password=sim"
    databases = None

    # Prepare the middlewear
    def __init__(self, get_response):
        self.get_response = get_response
        self.refresh()

    # calls after __call__
    # I modify here because __call__ is called before process_view, but we need to do refresh before other operations
    # so after refresh, we repeat the operation.
    # This function resposne to index function, the function of our home page.
    def process_view(self,request, index, view_args, view_kwargs):
        self.refresh()
        if not 'database' in request.session:
            # Database id
            request.session['database'] = 1

        # Inject the database information
        self.injectDatabase(request)

    # Get and return the response
    def __call__(self, request):
        # Execute before view functions
        # Set the default database if not already set (i.e. restart the server/ a new user access the website from the different browser)
        if not 'database' in request.session:
            # Database id
            request.session['database'] = 1

        # Inject the database information
        self.injectDatabase(request)

        # Render the view
        response = self.get_response(request)

        return response
    # set "sessions".
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

        # connect to database
        connection = psycopg2.connect(self.default)
        cursor = connection.cursor()
        cursor.execute(SQL)
        # dictionary: key is id, value is another dictionary which contains database connection information
        result = {}
        for row in cursor.fetchall():
            id = int(row[0])
            result[id] = {}
            result[id]['Name'] = row[1]
            result[id]['Connection'] = row[2]

        cursor.close()
        connection.close()

        return result


    # Refresh all relevent information
    def refresh(self):
        self.databases = self.getDatabases()