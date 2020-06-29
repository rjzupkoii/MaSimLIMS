##
# AppDatabase.py
#
# These are lower level database functions that may need to be executed.
##
import psycopg2

class AppDatabase:
    # Connection string for admin users
    ADMIN     = "host=masimdb.vmhost.psu.edu dbname=masim user={} password={}"
    CLONE     = "CREATE DATABASE {} WITH TEMPLATE template_masim"
    REFERENCE = "host=masimdb.vmhost.psu.edu dbname={} user=sim password=sim"


    def cloneDatabase(self, username, password, database):
        # Open the admin connection
        adminConnection = self.ADMIN.format(username, password)
        connection = psycopg2.connect(adminConnection)

        # Prepare the query
        query = self.CLONE.format(database)

        # Execute the query, this should be quick since the template database is empty
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(query)
        cursor.close()
        connection.close()


    def createConnectionString(self, database):
        return self.REFERENCE.format(database.lower())