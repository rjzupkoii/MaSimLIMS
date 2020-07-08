##
# AppDatabase.py
#
# These are lower level database functions that may need to be executed.
##
import psycopg2

from lims.shared import commitQuery

class AppDatabase:
    # Connection string for the application's database
    APPCONN   = "host=masimdb.vmhost.psu.edu dbname=masim user=sim password=sim"

    # Connection string for admin users
    ADMIN     = "host=masimdb.vmhost.psu.edu dbname=masim user={} password={}"

    # SQL to create the new database from the template
    CLONE     = "CREATE DATABASE {} WITH TEMPLATE template_masim"

    # Basic connection string to update
    REFERENCE = "host=masimdb.vmhost.psu.edu dbname={} user=sim password=sim"

    # View to add to the new database
    VIEW      = """CREATE OR REPLACE VIEW public.v_replicates AS SELECT c.filename, r.id, 
                   r.configurationid, r.seed, r.starttime, r.endtime, r.movement, 
                   r.endtime - r.starttime AS runningtime FROM sim.replicate r JOIN 
                   sim.configuration c ON c.id = r.configurationid;
                   ALTER TABLE public.v_replicates OWNER TO sim;"""


    def cloneDatabase(self, request, username, password, database):
        # Create the database
        self.executeSql(self.CLONE.format(database), self.ADMIN.format(username, password))
        
        # Create the view
        self.executeSql(self.VIEW, self.createConnectionString(database))

        # Insert the new connection into the databases table
        SQL = 'INSERT INTO app.database (name, connection) VALUES (%(name)s, %(connection)s)'
        commitQuery(request, SQL, {'name':database, 'connection':self.createConnectionString(database)}, self.APPCONN)


    # Return a valid connection string for the LIMS for the database name indicated
    def createConnectionString(self, database):
        return self.REFERENCE.format(database.lower())


    # Run and immediately commit the query provided
    def executeSql(self, query, connection):
        connection = psycopg2.connect(connection)
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(query)
        cursor.close()
        connection.close()
