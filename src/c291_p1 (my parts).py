import cx_Oracle
import os
import getpass
import datetime

# Works
# prints the header of each section prettily.
# msg has to be under 69 characters, inclusive.
def print_head(msg):
    right = 69 - len(msg)
    print("====", msg, "="*right+"====")
    return

# Works
# handles login and returns a connection
def handle_con():
    # connection variables
    username = ''
    password = ''
    host = 'gwynne.cs.ualberta.ca'
    port = '1521'
    SID = 'CRS'

    print_head("Login")
    while (1):
        try:
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            con = cx_Oracle.connect(username+'/'+password+'@'+host+':'+ \
                                    port+'/'+SID)
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            code = error.code
            msg = error.message
            #print("Oracle error code:", error.code)
            #print("Oracle error message:", error.message)
            if (code == 1017):
                print("Oracle error code:", error.code)
                print("Oracle error message:", error.message)
                print("You have entered an invalid username/password. " + \
                      "Please try again.")
            elif (code == 1005):
                print("Oracle error code:", error.code)
                print("Oracle error message:", error.message)
                print("You have entered an empty password. Please try " + \
                      "again.")
            else:
                print("Oracle error code:", error.code)
                print("Oracle error message:", error.message)   
        else:
            print("Message: Connection successful.")
            return con
    
    return

# Works. But there might be errors when dropping tables that did not exist
# previously.
# Probably not going to be part of final version.
def handle_setup(con):
    print("Please enter the setup sql and data file.")
    stop = False
    while (stop == False):
        try:
            setup_file_name = input("Setup file name: ")
            setup_file = open(setup_file_name, "r")

            # create database here
            sql_commands = setup_file.read()
            sql_commands = sql_commands.split(";")
            
            curs = con.cursor()
            for command in sql_commands:
                command = command.strip("\n")
                command = command.strip(" ")
                if (command != ""):
                    #print(">"+command+"<")
                    curs.execute(command)
                    
            con.commit()
            curs.close()
            setup_file.close()
        except IOError:
            print("File does not exist. Try again.")
        #except cx_Oracle.DatabaseError as e:
        #    print("Error executing setup sql file.")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            code = error.code
            msg = error.message
            print("Oracle error code:", error.code)
            print("Oracle error message:", error.message)        
        else:
            print("Database successfully setup.")
            stop == True
            break
        
    stop = False
    while (stop == False):
        try:
            data_file_name = input("Data file name: ")
            data_file = open(data_file_name, "r")
            
            # create database here
            sql_commands = data_file.read()
            sql_commands = sql_commands.split(";")
            
            curs = con.cursor()
            for command in sql_commands:
                command = command.strip("\n")
                command = command.strip(" ")
                #print(">"+command+"<")
                if (command != ""):
                    #print(">"+command+"<")
                    curs.execute(command)
            
            con.commit()
            curs.close()
            data_file.close()            
        except IOError:
            print("File does not exist. Try again.")
            #except cx_Oracle.DatabaseError as e:
            #    print("Error executing setup sql file.")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            code = error.code
            msg = error.message
            print("Oracle error code:", error.code)
            print("Oracle error message:", error.message)        
        else:
            print("Database successfully populated.")
            stop == True
            break
            
    return 

# Works
# returns a choice from main menu
def handle_main_menu():
    #os.system('clear')
    
    print_head("Main Menu")
    print("Please select one of the 4 main application programs or enter " + \
          "q to quit.")
    print("1 - Prescription")
    print("2 - Medical Test")
    print("3 - Patient Information Update")
    print("4 - Search Engine")

    choices = ['1', '2', '3', '4', 'q']

    while (1):
        choice = input("Please enter a choice between 1 to 4: ")
        if (choice == 'q'):
            return choice
        elif (choice == ""):
            print("Empty input detected. Try again.")
        elif (choice.isdigit() == False):
            print("Your input is not a number.")
        elif (choice not in choices):
            print(choice, "is not part of selections.")
        else:
            return choice

# Works
# checks for existence of person in table and returns a list of persons and
# their information
def get_person(con, item, id_type, table):
    """
    We need a special Boolean to determine if the function needs to do another
    query. If the functions receives a doctor's name, we need to first query
    this name from the patient table and then use the health_care_no to
    determine if this person is a doctor. The variable 'special' Boolean will
    determine if the second query is needed and proceed accordingly.
    """
    special = False
    curs = con.cursor()
    template = "SELECT * " + \
        "FROM {table} " + \
        "WHERE {attr} = {target}"
    
    if (table == 'doc'):
        if (id_type == 'num'):
            query = template.format(table = 'doctor', attr = 'employee_no', 
                                 target = str(item))
        elif (id_type == 'name'):
            query = template.format(table = 'patient', attr = 'name', 
                                 target = "'"+str(item)+"'")
            special = True
    elif (table == 'pat'):
        if (id_type == 'num'):
            query = template.format(table = 'patient', attr = 'health_care_no', 
                                 target = str(item))            
        elif (id_type == 'name'):
            query = template.format(table = 'patient', attr = 'name', 
                                 target = "'"+str(item)+"'")
    
    exist = False
    result = []
    
    try:
        #print(">"+query+"<")
        curs.execute(query)
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        code = error.code
        msg = error.message
        print("Oracle error code:", error.code)
        print("Oracle error message:", error.message)
    else:
        result = curs.fetchall()
        if (len(result) > 0):
            exist = True
            
        #print("Found:")
        #for row in result:
        #    print(row)
        
    curs.close()
    
    # only if person/patient exists first
    if (special == True and exist == True):
        # health_care_nos of all patients with provided name
        # stores ints
        id_num_list = []
        for row in result:
            id_num_list.append(row[0])
        
        result2 = []
        for id_num in id_num_list:
            curs = con.cursor()
            query = template.format(table = 'doctor', attr = 'health_care_no', 
                                    target = str(id_num))
            try:
                curs.execute(query)
                temp_result = curs.fetchall()
                result2.extend(temp_result)
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                code = error.code
                msg = error.message
                print("Oracle error code:", error.code)
                print("Oracle error message:", error.message)
                
            curs.close()
            
        #print("Found doctors:")
        #for row in result2:
        #    print(row)
            
        print("Message:", len(result2), "results found.")
        return result2
    else:
        print("Message:", len(result), "results found.")        
        return result

# Works
# returns one ID from a list of IDs
def select_person(people, person):
    print("Multiple", person+"s have been encountered. Please select one ID " + \
          "from below.\n")
    
    choices = []
    
    for p in people:
        print("ID: %s" %str(p[0]))
        choices.append(str(p[0]))
        print("\n")
    
    choice = input("ID = ")
    while (1):
        if (choice == ""):
            print("No empty input allowed.")
        elif (choice not in choices):
            print("That is not a valid choice.")
        else:
            return choice
        choice = input("ID = ")
        
    return None

# Works
# checks if an entered medical test exists in the database
# if exists, returns the type id of the test
def test_exist(con, test):
    template = "SELECT * " + \
        "FROM test_type " + \
        "WHERE test_name = {target}"
    
    query = template.format(target = "'"+test+"'")
    
    curs = con.cursor()
    result = []
    
    try:
        curs.execute(query)
        #print(">"+query+"<")
        result = curs.fetchall()
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        code = error.code
        msg = error.message
        print("Oracle error code:", error.code)
        print("Oracle error message:", error.message)
    
    curs.close()
    
    if (len(result) > 0):
        # return test id as a string
        return str(result[0][0])
    else:
        return False

# Works
# checks if patient can take test. Returns a Boolean value.
def can_take_test(con, patient, test):
    template = "SELECT * " + \
        "FROM not_allowed " + \
        "WHERE health_care_no = {target1} " + \
        "AND type_id = {target2}"
    
    query = template.format(target1 = patient, target2 = test)
    
    curs = con.cursor()
    result = []
    
    try:
        curs.execute(query)
        result = curs.fetchall()
    except cx_Oracle.DatabaseError as e:
        #print(">"+query+"<")
        error, = e.args
        code = error.code
        msg = error.message
        print("Oracle error code:", error.code)
        print("Oracle error message:", error.message)
    
    curs.close()
    
    if (len(result) == 0):
        return True
    else:
        return False    
    
    return False

# Works
# generates and returns a new id, which is 1 up from the last test record id
def generate_id(con):
    query = "SELECT MAX(test_id) " + \
        "FROM test_record"
    
    new_id = None
    curs = con.cursor()
    try:
        curs.execute(query)
        result = curs.fetchall()
        new_id = str(result[0][0]+1)        
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        code = error.code
        msg = error.message
        print("Oracle error code:", error.code)
        print("Oracle error message:", error.message)
        
    curs.close()
    
    return new_id

# =========================================================================================>
def prescribe(con, doctor, patient, test):
    curs = con.cursor()
    template = "INSERT INTO test_record " + \
        "VALUES ({test_id}, {type_id}, {patient_no}, {employee_no}, " + \
        "NULL, NULL, TO_DATE('{prescribe_date}', 'YYYY-MM-DD'), NULL)"
    
    new_id = generate_id(con)
    
    # get current date
    current_date = str(datetime.date.today())
    
    query = template.format(test_id = new_id, type_id = test, 
                            patient_no = patient, employee_no = doctor, 
                            prescribe_date = current_date)
    
    try:
        #print(query)
        curs.execute(query)
        con.commit()
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        code = error.code
        msg = error.message
        print("Oracle error code:", error.code)
        print("Oracle error message:", error.message)
    else:
        print("Prescription successfully inserted.")
        print("Database updated.")
    
    curs.close()
    
    # personal tests
    # start
    """
    query = "SELECT * " + \
        "FROM test_record"
    
    curs = con.cursor()
    curs.execute(query)
    result = curs.fetchall()
    for row in result:
        print(row)
    curs.close()
    """
    # end
    
    return

def prescription_mod(con):
    os.system('clear')

    print_head("Welcome to the Prescription Module")

    while (1):
        print("""
Please enter the following information:
    - <<doctor ID number/doctor name>>
    - <<patient healthcare number/patient name>>
    - <<test name>>
Press enter to continue.""")

        enter = input("")
        while (enter != ""):
            enter = input("")
            
        doctor = input("Please enter either the issuing doctor ID or the " + \
                       "doctor name: ")
        while (1):
            if (doctor == ""):
                print("No empty input allowed.")
            elif (not doctor.isdigit() and 
                  not isinstance(doctor, str)):
                print("You must enter an ID number or a name.")
            else:
                if (doctor.isdigit()):
                    result = get_person(con, doctor, 'num', 'doc')
                    if (len(result) == 0):
                        print("No doctor found. Please try again.")
                    elif (len(result) > 1):
                        doctor = select_person(result, 'doctor')
                        break
                    elif (len(result) == 1):
                        break
                else:
                    result = get_person(con, doctor, 'name', 'doc')
                    if (len(result) == 0):
                        print("No doctor found. Please try again.")
                    elif (len(result) > 1):
                        doctor = select_person(result, 'doctor')
                        break
                    elif (len(result) == 1):
                        doctor = str(result[0][0])
                        break                    
            doctor = input("Please enter either the issuing doctor ID or " + \
                           "the doctor name: ")

        patient = input("Please enter either the patient healthcare no. " + \
                        "or the patient name: ")
        while (1):
            if (patient == ""):
                print("No empty input allowed.")
            elif (not patient.isdigit()  and 
                  not isinstance(patient, str)):
                print("You must enter an ID number or a name.")
            else:
                if (patient.isdigit()):
                    result = get_person(con, patient, 'num', 'pat')
                    if (len(result) == 0):
                        print("No patient found. Please try again.")
                    elif (len(result) > 1):
                        patient = select_person(result, 'patient')
                        break
                    elif (len(result) == 1):
                        break                    
                else:
                    result = get_person(con, patient, 'name', 'pat')
                    if (len(result) == 0):
                        print("No patient found. Please try again.")
                    elif (len(result) > 1):
                        patient = select_person(result, 'patient')
                        break
                    elif (len(result) == 1):
                        patient = str(result[0][0])
                        break                                        
            patient = input("Please enter either the patient healthcare " + \
                            "no. or the patient name: ")

        test = input("Please enter the test name: ")
        while (1):
            if (test == ""):
                print("No empty input allowed.")
            elif (not isinstance(test, int) and not isinstance(doctor, str)):
                print("You must enter a proper test name.")
            else:
                # test if test exists
                test_exist_result = test_exist(con, test)
                if (test_exist_result == False):
                    print("Test does not exist. Please Try again.")
                else:
                    # test if patient can take this test
                    test = test_exist_result
                    result = can_take_test(con, patient, test)
                    if (result == False):
                        print("Sorry, this patient cannot take this test.")
                    else:
                        break
            test = input("Please enter the test name: ")

        print("Please review the following IDs related to each entered data.")
        print("Doctor: <<"+doctor+">>")
        print("Patient: <<"+patient+">>")
        print("Test: <<"+test+">>")
        
        proceed = input("Proceed with the above information? (y/n) ")
        proceed_check = False
        while (1):
            if (proceed.lower() == 'n'):
                break
            elif (proceed.lower() == 'y'):
                proceed_check = True
                break
            else:
                print("Please enter 'y' or 'n'.")       
            proceed = input("Proceed with the above information? (y/n)")
            
        if (proceed_check == True):
            prescribe(con, doctor, patient, test)

        again = input("Do you want to make another prescription? (y/n) ")
        if (again.lower() == 'n'):
            break
        elif (again.lower() != 'y'):
            print("Please enter 'y' or 'n'.")
        os.system('clear')
        
    curs = con.cursor()

    curs.close()
    
    return

def main():
    os.system('clear')

    print_head("Welcome to Health DB!")

    con = handle_con()

    # only needed for self testing?
    setup_check = input("Do you want to setup a new database? (y/n) ")
    if (setup_check.lower() == 'y'):
        handle_setup(con)

    while (1):
        choice = handle_main_menu()
        print(choice)
        if (choice == '1'):
            prescription_mod(con)
            os.system('clear')
        elif (choice == '2'):
            M = 0
        elif (choice == '3'):
            U = 0
        elif (choice == '4'):
            S = 0
        elif (choice == 'q'):
            con.close()
            os.system('clear')
            print("Thank you for using this DBMS.")
            break

    return

if __name__ == "__main__":
    main()
