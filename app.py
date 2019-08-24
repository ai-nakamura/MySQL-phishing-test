"""
Created: August 1, 2017
Last edit: August 18, 2017

MySQLdb_Engine

The purpose of this program is to connect to a given MySQL database using the MySQLdb library.
It's file dependencies are: (   views.py: displaying queries by printing to console,
                                user_interaction.py: interaction with user,
                                db_access.py: connecting and manipulating the database,
                                PhishingCampaignConfig.ini: stores information to access database
                            )



Main engine that connects the user and the database.
Is purposely restricted so that the user won't be able to accidentally manipulate and destroy the data directly through the endine

__author__ = "Ai Nakamura"
__version__ = "2.0.1"
__maintainer__ = "Ai Nakamura"
__email__ = "ainakamura513@gmail.com"
__status__ = "Production"
"""

# class for connectiong to database. Also takes care of inserting and updating data functions
from db_access import DbAccess
# class for User Interactions
from user_interactions import UserInteractions
# class for viewing queries in the console
from views import ViewQueries


class MySQLdb_Engine():
    def __init__(self):

        # prompts used throughout the program.
        self.prompts = {
            # general
            'initialGreeting' : "\nHello, welcome to KP Phishing db test\
                                 \nCurrent DATABASE: %s\
                                 \nHow may I assist you today?",
            'start' : "\nPlease choose from the following options:",
            'userInputPrompt' : "Please select your choice, or enter 'Q' to quit: ",

            # sub menu prompts
            'column_chosen' : "\nColumn selected:\t\t%s",
            'column_use' : "\nColumn(s) chosen are:\t",
            'column_chooseMore_yesNo' : ("\nColumn choosing done",
                                         "\nColumn choosing not done. Enter '0' at any time to end choosing.",
                                         "\nNo columns chosen. SELECT all? Enter 'Y' for yes, anything else to continue: "),

            # quit
            'quit_validate' : "\nAre you sure you want to quit? Enter Y to quit or any other key to stay: ",
            'quit_confirm' : ("Have a lovely day. Remember to treat yourself nicely today.",
                              "See ya later alligator! Always remember that you matter.",
                              "In a while crocodile! You're awesome just the way you are!",
                              "Thanks for spending time with me",
                              "Okie dokes. Remember, you're worth it",
                              "Tataa baby, and Hakuna Matata!",
                              "Alright then. Take care of yourself now, you hear?",
                              "Bye bye. Be a good experience.",
                              "See ya. Don't forget to be strong in the real way!"),
            'quit_deny' : "Glad to have you back!\n",

            # error
            'error_configuration' : "\nPlease reconfigure your connection information.",
            'error_emptyDB' : "\n***WARNING, the current database appears to be empty!!!***",
            'error_emptyTable': "\nThis table is empty.",
            'error_numOutOfRange' : "\nThis option is not available.",
            'error_notChar' : "\nThis is not a character.",
            'error_notNum' : "\nThis is not a number.",
            'error_duplicateColumn' : "\nColumn already selected.",
            'error_construction' : "Sorry, this area is under construction.\n",

            # menu options -- tuples of phrases to be parsed and presented on new lines to the user
            'menu_chosen': "\nMenu option %s chosen",
            'menu_start' : ("Insert/Update data", "View data", "Get Averages"),
            'menu_viewData' : ("Explain tables", "Show table contents", "Select table columns"),
            'menu_presets' : ("Presets will go here")
        }

        # CONNECT to db
        self.dbconn = DbAccess()
        # INSERT/UPDATE data in db
        self.insert = self.dbconn
        # VIEW data in db
        self.view = ViewQueries(self.prompts, self.dbconn)
        # INTERACT with user
        self.UI = UserInteractions(self.prompts)

        # set up tables_available
        # if tables_available.__len__() == 0, db is empty.
        self.db_empty = False
        self.tables_available = []
        for row in self.dbconn.query("SHOW TABLES"):
            self.tables_available.append(row[0])
        if self.tables_available.__len__() == 0:
            print (self.prompts['error_emptyDB'])
            self.db_empty = True

        # run program
        self.engine()

    #------------ user interface ----------------#
    '''
    Main engine that runs the program.
    Guides the user through a menu to determine which query to run and display in the console
    Current limitation: - User does not have the ability to back out of a chosen menu.
                            - Possibly can implemented within 'UI.get_user_input' method?
                        - Server in use is ver. 5.1.73 and proved incompatible with ver. 5.7.18
    '''
    def engine(self):

        # initial greeting that displays db name
        db_name = self.dbconn.query("SELECT DATABASE()")[0][0]
        print(self.UI.prompts['initialGreeting'] % db_name)

        while True:
            # main menu
            userChoice_mainMenu = self.UI.get_user_input(self.prompts['menu_start'])
            print(self.prompts['menu_chosen'] %str(userChoice_mainMenu))

            # option 1. Insert/Update new data
            if userChoice_mainMenu == 1:
                self.__insert_new_data(userChoice_mainMenu)

            # option 2: View data
            elif userChoice_mainMenu == 2:
                if self.db_empty == True:
                    print(self.prompts['error_emptyDB'])
                else:
                    self.__select_table_columns(userChoice_mainMenu)

            # option 3: Get averages
            elif userChoice_mainMenu == 3:
                if self.db_empty == True:
                    print(self.prompts['error_emptyDB'])
                else:
                    print("get averages")

            # place holder for future enhancements

    '''
    Inserts new data as supplied in 'PhishingCampaignConfig.ini' file
    Users will be given the option to choose which table to update in future versions
    '''
    def __insert_new_data(self, user_choice):

        print("inserting new data...")
        self.dbconn.insert_data('phish_file', 'phish_criteria_csv', 'phish_criteria_db', 'PHISHING_DATA')
        # elif choose emp:
        #     self.dbconn.insert_data('employee_file', 'employee_criteria_csv', 'employee_criteria_db', 'EMPLOYEE_DATA')
        # later on include more hardcoded tables as needed

    '''
    Function for menu item 2: View data
    Covers MySQL queries for EXPLAIN, SELECT *, and SELECT [specific columns] to see data contents
    Additionally gives users the option to LIMIT data returned
    
    :param user_choice: int of the menu choice user picked.
                        Will always be the corresponding number of how user got here in the first place.
    '''
    def __select_table_columns(self, user_choice):
        # choose which sub choice
        userChoice_option3 = self.UI.get_user_input(self.prompts['menu_viewData'])
        print(self.prompts['menu_chosen'] % (str(user_choice) + "." + str(userChoice_option3)))

        # choose which table to act on
        optChoice_table = self.UI.get_user_input(self.tables_available)
        table = self.tables_available[optChoice_table - 1]
        print("Table : " + table)

        # option 3.1: Explain tables
        if userChoice_option3 == 1:
            sql = " EXPLAIN " + table
            self.view.parse_EXPLAIN(self.dbconn.query(sql))

        # option 3.2: Show table contents
        if userChoice_option3 == 2:
            sql = self.view.apply_LIMIT(" SELECT * FROM " + table, table)
            self.view.parse_SELECT(self.dbconn.query(sql), table)

        # option 3.3: Select table columns
        if userChoice_option3 == 3:
            # pull column names to choose from
            columnNames = self.view.label_maker(table)
            # get proper column indexes, then store the string column names into a sorted order
            selected_column_indexes = self.UI.choose_columns(columnNames)
            columns = [columnNames[i] for i in selected_column_indexes]
            # print: columns in use, LIMIT applied, then result
            print(self.prompts['column_use'] + (', ').join(columns))
            sql = self.view.apply_LIMIT(" SELECT " + (', ').join(columns) + " FROM " + table, table)
            self.view.parse_SELECT(self.dbconn.query(sql), table, columns)



MySQLdb_Engine()