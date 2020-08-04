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
        cursor.execute(SQL, {'replicateId': replicateId})
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
        if running:
            SQL = """
                SELECT filename, starttime, movement,
                    CASE WHEN endtime IS NULL THEN (now() - starttime) ELSE runningtime END AS runningtime
                FROM v_replicates {} ORDER BY starttime DESC LIMIT %(limit)s"""
        else:
            SQL = """
                SELECT id, filename, starttime, endtime, movement,
                    CASE WHEN endtime IS NULL THEN (now() - starttime) ELSE runningtime END AS runningtime
                FROM v_replicates {} ORDER BY starttime DESC LIMIT %(limit)s"""
        WHERE = "WHERE (now() - starttime) <= interval '3 days' AND endtime IS NULL"

        # Update the query and return the results
        append = WHERE if running else ""
        return selectQuery(request, SQL.format(append), {'limit': limit})
    

    # Get configurations that associate with specific study id.
    @staticmethod
    def getStudyConfigurations(request,studyid = None):
        # If studyid is a number.
        if studyid:
            SQL = """
                SELECT configuration.filename, 
                concat('(', ncols, ', ', nrows, ', ', xllcorner, ', ', yllcorner, ', ', cellsize, ')') as spatial, count(replicate.id), configuration.id
                FROM configuration left join replicate on replicate.configurationid = configuration.id 
                WHERE studyid = %(id)s group by configuration.id order by configuration.id"""
            return selectQuery(request, SQL, {'id':studyid})
        # If studyid is False.
        else:
            SQL="""
                SELECT configuration.filename, 
                concat('(', ncols, ', ', nrows, ', ', xllcorner, ', ', yllcorner, ', ', cellsize, ')') as spatial, count(replicate.id), configuration.id 
                FROM configuration left join replicate on replicate.configurationid = configuration.id 
                WHERE studyid is NULL group by configuration.id order by configuration.id"""
            return selectQuery(request, SQL)

    
    # Get replicates that associate with specific study id
    @staticmethod
    def getStudyReplicates(request,studyid = False):
        # if studyid is a number
        if studyid:
            SQL = """
                SELECT v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime FROM study 
                LEFT JOIN configuration ON configuration.studyID = %(id)s INNER JOIN v_replicates ON v_replicates.configurationid = configuration.id 
                WHERE study.id = %(id)s ORDER BY v_replicates.starttime desc"""
            return selectQuery(request, SQL,{'id':studyid})
        else:
            SQL = """
                SELECT v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime
                FROM configuration INNER JOIN v_replicates ON v_replicates.configurationid = configuration.id WHERE studyid IS NULL ORDER BY v_replicates.starttime desc"""
            return selectQuery(request,SQL)


    @staticmethod
    def insertStudy(request, name):
        SQL = 'INSERT INTO study (name) VALUES (%(name)s)'
        commitQuery(request, SQL, {'name':name})


    # Get the replicates that have been running longer than two days
    @staticmethod
    def getLongRunningReplicates(request):
        SQL = """
            SELECT filename, starttime, movement, (now() - starttime) AS runningtime
            FROM v_replicates 
            WHERE endtime IS null AND (now() - starttime) > interval '2 days'
            ORDER BY runningtime DESC"""
        return selectQuery(request, SQL)


    # Get list of study names, count of study configurations and replicates; as well as unassigned counts
    @staticmethod
    def getStudies(request):
        SQL = """
            SELECT s.name,s.id,COUNT(DISTINCT c.id) configs, COUNT(DISTINCT r.id) replicates 
            FROM sim.study s 
                LEFT JOIN sim.configuration c ON c.studyid = s.id 
                LEFT JOIN v_replicates r on r.configurationid = c.id 
            GROUP BY s.id
            UNION
            SELECT CASE WHEN name IS NULL THEN 'Unassigned' ELSE name END, studyid,configs, replicates 
            FROM (
                SELECT s.id, studyid, s.name, COUNT(DISTINCT c.id) configs, COUNT(DISTINCT r.id) replicates
                FROM sim.configuration c 
                    LEFT JOIN sim.replicate r ON r.configurationid = c.id 
                    LEFT JOIN sim.study s ON s.id = c.studyid 
                GROUP BY s.id, studyid, s.name) iq order by id"""
        return selectQuery(request, SQL)
            

    # Get replicates that associate with configuration
    @staticmethod
    def getConfigReplicate(request, id = False):
        # If id is a number
        if id:
            SQL = """
                SELECT v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime
                FROM v_replicates WHERE configurationid = %(id)s ORDER BY v_replicates.id"""
            return selectQuery(request,SQL, {'id': id})
        else:
            SQL = """
                SELECT v_replicates.filename, v_replicates.starttime, v_replicates.endtime, v_replicates.movement, v_replicates.runningtime
                FROM v_replicates WHERE configurationid IS NULL ORDER BY v_replicates.id"""
            return selectQuery(request,SQL)

    
    # Get notes that associate with study
    @staticmethod
    def getStudyNotes(request, id):
        SQL = """
            SELECT * FROM notes WHERE studyid = %(id)s ORDER BY date DESC"""
        return selectQuery(request, SQL,{"id":id})


    # Insert notes
    @staticmethod
    def insertNotes(request, notes, user,studyId):
        SQL = """insert into notes (data, "user", date, studyid) values (%(data)s,%(user)s,now(),%(studyid)s)"""
        commitQuery(request,SQL, {'data':notes, 'user': user, 'studyid':studyId})

    
    @staticmethod
    def deleteNotes(request, id):
        SQL = """delete from notes where id = %(id)s"""
        commitQuery(request,SQL, {"id":id})