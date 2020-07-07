##
# AppDatabase.py
#
# These are lower level database functions that may need to be executed.
##
from psycopg2 import sql
import psycopg2

from lims.shared import commitQuery

class AppDatabase:
    # Connection string for the application's database
    APPCONN   = """host=masimdb.vmhost.psu.edu dbname=masim user=sim password=sim"""

    # Connection string for admin users
    ADMIN     = """host=masimdb.vmhost.psu.edu dbname=masim user={} password={}"""

    # SQL to create the new database from the template
    CLONE     = """CREATE DATABASE {database} WITH TEMPLATE template_masim"""

    # Basic connection string to update
    REFERENCE = """host=masimdb.vmhost.psu.edu dbname={database} user=sim password=sim"""

    # View to add to the new database
    VIEW      = """CREATE OR REPLACE VIEW public.v_replicates AS SELECT c.filename, r.id, 
                   r.configurationid, r.seed, r.starttime, r.endtime, r.movement, 
                   r.endtime - r.starttime AS runningtime FROM sim.replicate r JOIN 
                   sim.configuration c ON c.id = r.configurationid;
                   ALTER TABLE public.v_replicates OWNER TO sim;"""


    def cloneDatabase(self, request, username, password, database):
        # Open the admin connection
        # sample: stmt = sql.SQL("""SELECT COUNT(*) FROM (SELECT 1 FROM {table_name} LIMIT {limit}) AS limit_query""").format(table_name = sql.Identifier(table_name),limit = sql.Literal(limit),)

        # Here may not have sql injection problem, because here is connection.
        adminConnection = self.ADMIN.format(username, password)

        connection = psycopg2.connect(adminConnection)
        
        
        databaseConnection = self.createConnectionString(database).as_string(connection)
        # Prepare the query
        # This syntax may have injection problem and I cahnge it.
        # query = self.CLONE.format(database)
        query = sql.SQL(self.CLONE).format(database=sql.Identifier(database),)

        # Execute the query, this should be quick since the template database is empty
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(query)

        # Add the view to the database
        cursor.execute(VIEW)
        # Clean-up and return
        cursor.close()
        connection.close()
        # Insert the new connection into the databases table
        SQL = 'INSERT INTO app.database (name, connection) VALUES (%(name)s, %(connection)s)'
        # I modify here because no app is created and because of sql injection.
        commitQuery(request, SQL, {'name':database, 'connection':databaseConnection}, self.APPCONN)


    def createConnectionString(self, database):
        #return self.REFERENCE.format(database.lower())
        return sql.SQL(self.REFERENCE).format(database = sql.Identifier(database.lower()),)

