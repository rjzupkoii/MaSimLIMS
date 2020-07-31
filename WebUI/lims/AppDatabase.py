##
# AppDatabase.py
#
# These are lower level database functions that may need to be executed.
##
import psycopg2

from lims.shared import commitQuery, selectQuery

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


    # Deletes the replicate indicated from the database, returns True if the operation was successful
    def deleteReplicate(self, request, replicateId):
        # Open the connection
        connection = psycopg2.connect(request.session['dbconnection'])
        connection.autocommit = True
        cursor = connection.cursor()

        # Run the stored procedure
        SQL = 'CALL delete_replicate(%(replicateId)s'
        cursor.execute(sql, {'replicateId': replicateId})

        # Parse the messages
        success = False
        for notice in connection.notices:
            if "NOTICE:  Complete" in notice.contains: success = True

        # Clean-up and return
        cursor.close()
        connection.close()
        return success


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


    # Get the replicates based upon if they are running (or not) with an upper limit for how many (default 1000)
    @staticmethod
    def getReplicates(request, running, limit = 1000):
        SQL = """
            SELECT id, filename, starttime, endtime, movement,
                CASE WHEN endtime IS NULL THEN (now() - starttime) ELSE runningtime END AS runningtime
            FROM v_replicates {} ORDER BY starttime DESC LIMIT %(limit)s"""
        WHERE = "WHERE (now() - starttime) <= interval '3 days' AND endtime IS NULL"

        # Update the query and return the results
        append = WHERE if running else ""
        return selectQuery(request, SQL.format(append), {'limit': limit})
    

    # Get the replicates that have been running longer than two days
    @staticmethod
    def getLongRunningReplicates(request):
        SQL = """
            SELECT id, filename, starttime, endtime, movement, (now() - starttime) AS runningtime
            FROM v_replicates 
            WHERE endtime IS null AND (now() - starttime) > interval '2 days'
            ORDER BY runningtime DESC"""
        return selectQuery(request, SQL)


    # Get list of study names, count of study configurations and replicates; as well as unassigned counts
    @staticmethod
    def getStudies(request):
        SQL = """
            SELECT s.id, s.name, COUNT(DISTINCT c.id) configs, COUNT(DISTINCT r.id) replicates 
            FROM sim.study s 
                LEFT JOIN sim.configuration c ON c.studyid = s.id 
                LEFT JOIN v_replicates r on r.configurationid = c.id 
            GROUP BY s.id
            UNION
            SELECT studyid, CASE WHEN name IS NULL THEN 'Unassigned' ELSE name END, configs, replicates 
            FROM (
                SELECT s.id, studyid, s.name, COUNT(DISTINCT c.id) configs, COUNT(DISTINCT r.id) replicates
                FROM sim.configuration c 
                    LEFT JOIN sim.replicate r ON r.configurationid = c.id 
                    LEFT JOIN sim.study s ON s.id = c.studyid 
                GROUP BY s.id, studyid, s.name) iq order by id"""
        return selectQuery(request, SQL)
            
