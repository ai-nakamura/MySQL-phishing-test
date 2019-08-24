import csv
import MySQLdb
import os
import string
import random
from datetime import datetime
from config_parse import ConfigParse

class DbAccess():
    # Database Constructor initializing MySQL Connection
    def __init__(self):
        self.conn = self.mysqlConnect()

    # Connect to MySQL DB
    def mysqlConnect(self):

        config = ConfigParse().get_config()

        # Store MYSQL DB Credentials
        host = config.get('mysql', 'ip_address')
        port = config.get('mysql', 'socket')
        db = config.get('mysql', 'dbname')
        user = config.get('mysql', 'username')
        passwd = config.get('mysql', 'password')

        # Convert 'port' from string to int
        port = int(port)

        try:
            # Connect to the MySQL DB
            conn = MySQLdb.Connection(
                host=host, port=port, user=user, passwd=passwd, db=db)
        except MySQLdb.Error:
            print("ERROR Connecting to MySQL DB. Please check MySQL Connection Details in Config file!")
            exit(1)

        return conn

    # Close Connection
    def mysqlCloseConnection(self):
        # Check if MySQL connection open
        if self.conn:
            # Check if MySQL cursor for executing SQL statements is open
            if self.conn.cursor():
                # Close MySQL Cursor
                self.conn.cursor.close()
            # Close MySQL Connection
            self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    # Run desired MySQL Query, with desired SQL Statement
    def query(self, sql):
        # Create Cursor to execute MySQL Statement
        curs = self.conn.cursor()
        try:
            # Execute MySQL Statement and Commit change to DB
            curs.execute(sql)

            # Throw error if Query fails for whatever reason
            self.commit()

        except Exception as e:
            # Rollback DB to previous version
            self.rollback()

            # print error
            print(e)
            return None

        # Return Query Results
        return curs.fetchall()

    #Parent Function for inserting data from CSV file into a table in the MySQL DB
    def insert_data(self, file_name, criteriaCsv, criteriaDb, tableName):
        config = ConfigParse().get_config()

        data = self.read_data(file_name, criteriaCsv)
        self.insert_db(config, data, criteriaCsv, criteriaDb, tableName)



    # Read in data from CSV file.
    # Config: path to files, file_name: name of csv, config_criteria: criteria to filter
    def read_data(self, file_name, config_criteria):
        config = ConfigParse().get_config()

        # Store phishing_campaign CSV File Path
        file_name = config.get('csv', file_name)
        file_loc = os.path.abspath(file_name)

        data_columns = config.get('data_columns', config_criteria)
        criteria = data_columns.split(', ')
        # Test to make sure File is .csv
        if file_name[-4:] != '.csv':
            print(
                "\nWe can only upload phishing data and employee data from a CSV File! Please replace file with CSV and update Config File!\n")
            exit(1)
        else:
            try:
                data = []
                i = 0
                data_file = open(file_loc, 'r')
                reader = csv.reader(data_file)

                #Instantiate local Variable to be updated with value as we loop through the rows of Phishing Data
                email_campaign = ''

                for row in reader:
                    if i == 0:
                        master_header = row
                    else:
                        real = {}
                        dicc = dict(zip(master_header, row))  # creates a dict of all columns from csv
                        for key in dicc.keys():
                            if key in criteria:  # matches key with employee header needed
                                real[key] = dicc[key]  # new dict of columns needed for employee table
                                real_key = self.test_phish_data(key, real[key], i)
                                real[key] = real_key

                                # create unique primary key for each row in PHISHING_DATA 'EMAIL_CAMPAIGN
                                if key == "Email":
                                    email_campaign = real[key] + email_campaign
                                elif key == "Phish Campaign":
                                    email_campaign = email_campaign + real[key]

                        real['EMAIL_CAMPAIGN'] = email_campaign
                        email_campaign = ""
                        data.append(real)
                    i += 1
                return data
            except IOError:
                # Checks if user inputted a File that does not exist
                print("\nERROR: File with phishing data or employee data cannot be opened at this location; please double check file location and permission to this directory!\n")
                exit(1)


    #Converts data in Phishing CSV to format needed to store in MYSQL DB
    def test_phish_data(self, key, real_key, row):
        # Checks for boolean column value and converts to tinyint for mysql insertion
        if key in ("Reported Phish?", "Clicked Link?", "Mobile?"):
            if real_key.lower().strip() in ("yes", "true"):
                real_key = "1"
            elif real_key.lower().strip() in ("no", "false"):
                real_key = "0"
            elif real_key == "":
                # If NULL set to FALSE
                real_key = "0"
            else:
                #Throws error if Phish CSV Boolean Column holds anything but a boolean or NULL!
                print("Row #" + row + ": Column - [" + key + "] is not null nor a boolean in the CSV! Please fix CSV!")
                exit(1)

        # Convert Non-Null PST timestamps to have mysql timestamp format: (*M/*D/YYYY *H:MM:SS --> YYYY-MM-DD HH:MM:SS)
        elif key in ("Last Email Status Timestamp", "Reported Phish Timestamp", "Clicked Link Timestamp") and (real_key != ""):
                try:
                    # Break TimeStamp into date and time objects
                    tmp_date, tmp_time = real_key.split(" ")

                    # Break Date into Day, Month, and Year objects
                    tmp_month, tmp_day, tmp_year = tmp_date.split("/")

                    # Reorg the format of the TimeStamp
                    date_string = tmp_year + "-" + tmp_month + "-" + tmp_day + " " + tmp_time

                    real_key = date_string
                except:
                    # Throws error if Phish CSV Timestamp is formatted differently then anticipated!
                    print("Row #" + str(row) + ": " + str(key) + " is misformatted in the CSV! Should be *M/*D/YYYY *H:MM ")
                    print("(Value = " + str(real_key) + ")")
                    exit(1)

        return real_key

    # Insert data into employee and phishing_data table
    def insert_db(self, Config, data, criteriaCsv, criteriaDb, tableName):
        sqlInsertCount = 1
        csvList = Config.get('data_columns', criteriaCsv)
        dbList = Config.get('data_columns', criteriaDb)

        csvCriteria = csvList.split(', ')
        dbCriteria = dbList.split(', ')

        sqlData = dict(zip(csvCriteria, dbCriteria))
        
        dbInitialCount = self.query("Select COUNT(*) from phishing.PHISHING_DATA")

        for row in data:
            insert = {}
            for oo in row.keys():
                if type(row[oo]) != bool:
                    insert[sqlData[oo]] = row[oo].replace("'", "").replace('"', "")
            names = ', '.join(insert.keys())
            values = "'" + "', '".join(insert.values()) + "'"

            #Handles duplicate rows and updates if old key exists
            updateNames = insert.keys()
            updateValues = insert.values()
            updateRow = ""
            i = 0
            for name in updateNames:
                updateRow = updateRow + name + ' = ' + "'" + updateValues[i] + "'" + ", "
                i += 1
            updateRow = updateRow[:-2]
            
            sql = "INSERT INTO " + tableName + "(%s) VALUES (%s)" % (
            names, values) + "ON DUPLICATE KEY UPDATE " + updateRow
            if (sqlInsertCount % 10 == 0):
                print("Inserting row " + str(sqlInsertCount) + " into " + tableName + " table.")
            self.query(sql)
            

            sqlInsertCount += 1

        dbFinalCount = self.query("Select COUNT(*) from phishing.PHISHING_DATA")

        dbDiffCount = int(dbFinalCount[0][0]) - int(dbInitialCount[0][0])

        dbUpdatedCount = sqlInsertCount - dbDiffCount - 1    
        print("Inserted " + str(dbDiffCount) + " rows into  " + tableName + " table.")
        print("Updated " + str(dbUpdatedCount) + " rows in " + tableName + " table.")