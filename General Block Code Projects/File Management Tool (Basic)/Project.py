import os

while True:
    def Create_File():
        try:
            filename = str(input("Enter the filename to create: "))
            file = open(filename, 'x')
            
        except FileExistsError:
            print(f"{filename} file alredy Exist")
            
        except Exception as e:
            print("An unknown error occurred, please try again")
        
    def Read_File():
            
        try:
            filename = str(input("Enter the filename to read: "))
            file = open(filename, 'r')
            print(f"Content in file: \n {file.read()}")
            file.close()
        except FileNotFoundError:
            print("File Not Found, please try again")
            
        except Exception as e:
            print("An unknown error occurred, please try again")
            
    def Edit_File():
        
        try:
            filename = str(input("Enter the filename to edit: "))
            file = open(filename, 'w')
            cont =  str(input("Enter the Content: "))
            write = file.write(cont)
            print(f"Content written: {write}")
        except FileNotFoundError:
            print("File Not Found, please try again")
        except Exception as e:
            print("An unknown error occurred, please try again")
        
    def Delete_File():
            
        try:
            filename = str(input("Enter the filename to delete: "))
            file = os.remove(filename)
            print(f"deleted: {filename}")
        except FileNotFoundError:
            print("File Not Found, please try again")
        except Exception as e:
            print("An unknown error occurred, please try again")
            
    def view_file():
        
        if not files:
            print("No Files Found")
            
        else:
            files = os.listdir()
            for f in files:
                print(f"Files in Directory: {f}")
                
    break
        
        

        

# Choices
while True:
    print("1. Create a new File")
    print("2. Read a File")
    print("3. Edit a File")
    print("4. Delete a File")
    print("5. View all Files on Directory")
    
    Input = int(input("Enter Opration choice to Perform: "))

    if Input == range(0, 5):
    
        match Input:
            
            case 1:
                Create_File()
            
            case 2:
                Read_File()
                
            case 3:
                Edit_File()
                
            case 4:
                Delete_File()
                
            case 5:
                view_file()
                
    else:
        print("Invalid Choice")
