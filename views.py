# -----------------------------------------------------------------------------------#
'''
Created: August 1, 2017
Last edit: August 18, 2017

This class contains the functions used to display the queries back to the user in the console.

__author__ = "Ai Nakamura"
__version__ = "2.0.1"
__maintainer__ = ""
__email__ = "ainakamura513@gmail.com"
__status__ = "Production"
'''

class ViewQueries():
# ----- Queries ---------------------------------------------------------------------#
    def __init__(self,prompts, dbconn):
        self.prompts = prompts
        self.dbconn = dbconn


    '''
    ***NOTE: DEPRECIATED August 1st -- will send queries to DbAccess() class from db_access.py***
    This is the function that runs the query itself.
    Return the raw nested tuple for the next function to parse into a printable string.
    This method *only* runs the mysql query that is directly fed into it.
    '''
    '''
    def runQuery(cursor, mysqlQuery):
        try:
            print ("Running query: %s\n" % mysqlQuery)
            cursor.execute('%s' % mysqlQuery)
            return cursor.fetchall()
        except MySQLdb.Error as err:
            print (err)
            print ("something went wrong with query: %s" % mysqlQuery)
            return
    '''


    '''
    Returns a list of strings of the column labels.
    Can return either all or selected columns
    
    :rtype labels: a list of the column names to be used as a label to be printed at the top of the printed result
    '''
    def label_maker(self, table, extra='', columns='*'):
        labels = []
        rows = self.dbconn.query("EXPLAIN %s" % str(table))
        for row in rows:
            if not columns == '*':
                for c in columns:
                    if c in row:
                        labels.append(extra + row[0] + extra)
            else:
                labels.append(extra + row[0] + extra)
        return labels


    '''
    Modifies the given query with a limit if so desired
    Current limitation - if user presses 'enter', the except triggers and the function executes with no limit
    
    :rtype newSql: returns the provided mysqlQuery with the LIMIT query appended to the end if desired
    '''
    def apply_LIMIT(self, mysqlQuery, table):
        newSql = mysqlQuery
        num_rows = self.dbconn.query("SELECT COUNT(*) FROM " + table)[0][0] # <-- num_rows = ((#,)) tuple in tuple returned
        try:
            impose_limiter = "\nWould you like to add a LIMIT? The table %s has %i rows. Enter '0' for no limit: "
            limit = int(input(impose_limiter % (table, num_rows)))
            if limit < num_rows and limit > 0:
                newSql += " LIMIT " + str(limit)
                print("Limit chosen for {} rows".format(limit))
            elif limit == 0:
                print("No limit added, printing all {} rows.".format(num_rows))
        except:
            print("Error with " + str(self.__class__.__name__) + "'s limit applier")
        return newSql


    # -----------------------------------------------------------------------------------#
    '''
    This is the printer section.
    It parses the fetched data into a readable string format that is then printed to the console.
    Later editions should be able to modify this section fairly easily to be able to print to file.
    '''
    # ----- Parse query into readable output --------------------------------------------#

    '''
    EXPLAIN table_name
    Prints a string representing the EXPLAIN query
    '''
    def parse_EXPLAIN(self, tup):
        print('{:<32}{:<24}{:<12}{:<12}{:<12}{:<12}'.format("::Field::",
                                                            "::Type::",
                                                            "::Null::",
                                                            "::Key::",
                                                            "::Default::",
                                                            "::Extra::"))
        for row in tup:
            print('  {:<32}{:<24}{:<12}{:<12}{:<12}{:<12}'.format(*row))


    '''
    SELECT arg FROM table_name
    Prints a string representing the SELECT query
    Is made to be able to return an undetermined number of columns
    
    :param tup - the tuple or list to get main data from
    :param table - the list of name(s) of the columns to use
    :param columns - to be used by label_maker to determine if all columns should be retrieved or not
    '''
    def parse_SELECT(self, tup, table, columns='*'):

        # check if table isn't empty
        if len(tup) == 0:
            print (self.prompts['error_emptyTable'])
            return

        list = []
        maxOfColumns = []

        # add the header and the data together into one list
        list.append(self.label_maker(table, "::", columns))
        for row in tup:
            list.append(row)

        # find max length of all items in every column for spacing later
        for t in tup[0]:
            maxOfColumns.append(8)
        for t in list:
            for i in range(0, len(t)):
                if maxOfColumns[i] < len(str(t[i])):
                    maxOfColumns[i] = len(str(t[i]))

        # print out the data

        # set up spacing using the header
        toPrintSpace = ""
        for i in list[0]:
            toPrintSpace += '{:<%s}' % ((maxOfColumns[list[0].index(i)]) + 4)

        # creates one string from the given list and prints them on a per row basis
        layer = []
        buffer = ""
        for row in list:
            for item in row:
                layer.append(str(item))
            print(buffer + toPrintSpace.format(*layer))
            # print buffer + toPrintSpace.format(*row) to give clean look to columns
            buffer = "  "
            del layer[:]

# -----------------------------------------------------------------------------------#
