'''
Created: August 1, 2017
Last edit: August 18, 2017

Ths is the class that takes care of User Interaction.
Anything related to asking the user to do anything will be in this class

__author__ = "Ai Nakamura"
__version__ = "2.0.1"
__maintainer__ = "Ai Nakamura"
__email__ = "ainakamura513@gmail.com"
__status__ = "Production"

'''
# This is a secret :) don't remove it!
from random import randint

class UserInteractions():
# ------------ Prompts ------------------------------------------------------------#

    def __init__(self, prompts):
        self.prompts = prompts

    '''
    Function to display given menu prompt to user in a numbered list format and returns a valid user choice
    Also serves to terminate the entire program if user enters 'Q'
    
    :param menuPrompt: either a list or tuple of the prompts to display
    :param isMultipleColumns: True if returning '0' is a valid option (for chooseColumn menu option only)
    :rtype: queryChoice : int - option number of user's choice (not the index, will be index + 1)
    '''
    def get_user_input(self, menu_prompt, is_multiple_columns=False):
        queryChoice = -1
        # run indefinitely until a proper choice is made
        while queryChoice < 0:
            try:
                print(self.prompts['start'])
                for index in range(0, len(menu_prompt)):
                    print("%s. " % (index + 1) + menu_prompt[index])
                choice = (input(self.prompts['userInputPrompt']))

                # Check if user wants to end program
                if choice.upper() == 'Q':
                    raise IOError
                # Determine if the user given choice if within the range of menu_prompt given.
                else:
                    queryChoice = int(choice)
                    if type(menu_prompt) == int:
                        max_range = menu_prompt
                    else:
                        max_range = len(menu_prompt)
                    # for multiple column selection only.
                    # returns a '0' to indicate that the user is finished making column selections
                    if queryChoice == 0 and is_multiple_columns == True:
                        return 0
                    elif queryChoice > max_range or queryChoice <= 0:
                        raise TypeError

            except(IOError):
                # Runs when the user wants to quit. Prompts the user to confirm to quit
                q = str(input(self.prompts['quit_validate']))
                if q.upper() == 'Y':
                    quit_num = randint(0, len(self.prompts['quit_confirm'])-1)
                    print(self.prompts['quit_confirm'][quit_num])
                    raise SystemExit
                else:
                    print(self.prompts['quit_deny'])
            except(TypeError):
                queryChoice = -1
                print(self.prompts['error_numOutOfRange'])
            except:
                print(self.prompts['error_notNum'])

            else:
                if queryChoice > 0: break

        # returns the user's choice as the number from the menu (will be index + 1)
        return (queryChoice)


    '''
    Function for choosing specific columns when using the "Select columns" option.
    The user is prompted to pick a column, or enter '0' to indicate that they are done.
    The list will not append any column that has already been selected.
    Current limitations:    - There's no option for users to select all in case they ended up in the wrong menu
                                - Would be solved if backing out was an option
                            - Function won't end even if the user has manually selected all columns, still must enter '0'
    :param column_names: prompt to be passed to getUserInput where it'll be treated as a menu
    :rtype: desiredColumnIndexes: list - unordered list of index of desired columns
    '''
    def choose_columns(self, column_names):

        desired_column_indexes = []
        while True:

            # pick a column
            column_choice = self.get_user_input(column_names, True)

            # if 0, end function or give option to return all if desired_columns_indexes is empty
            if column_choice == 0:
                # Option to return all columns
                if desired_column_indexes.__len__() == 0:
                    select_all =  input(self.prompts['column_chooseMore_yesNo'][2])
                    if select_all.upper() == 'Y':
                        return range(0, len(column_names))
                    else:
                        print(self.prompts['quit_deny'])
                # End function by breaking out of loop
                else:
                    print(self.prompts['column_chooseMore_yesNo'][0])
                    break
            else:
                # check for duplicates
                if column_choice - 1 not in desired_column_indexes:
                    print(self.prompts['column_chosen'] % column_names[column_choice - 1])
                    desired_column_indexes.append(column_choice - 1)
                else:
                    print(self.prompts['error_duplicateColumn'])
                desired_column_indexes.sort()
                print(self.prompts['column_use'] + ', '.join([column_names[i] for i in desired_column_indexes]))
                print(self.prompts['column_chooseMore_yesNo'][1])
        # returns the desired column indexes sorted
        return desired_column_indexes

