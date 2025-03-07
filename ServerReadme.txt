GOOD DAY 
This is the ServerReadme file which explains how to install all the software required to run the Homicide Media Analysis dashboard and database. It also explains how to create a new database called homicide_main

Software required:
1. PostgreSQL --> an open sources Database Management Tool used to create the database. To install, please follow the procedures in this link https://www.postgresql.org/download/
2. Python programing language --> this is needed to execute the code required for the dashboard and the database. To download and install, please follow the procedures in this link   https://phoenixnap.com/kb/how-to-install-python-3-windows
3. VS code --> This is the preferred IDE required to run the code. To download and install, please use the procedure below https://code.visualstudio.com/docs/setup/windows

Please install all the above mentioned software first 

Server Setup Guide
1. When installing PostgreSQL, you will be required to enter a password, please remember that password.
2. Once PostgreSQL is installed, go to search feature in your Operating System and search for pgAdmin 4. pgAdmin 4 is a GUI interface for PostgreSQL. 
3. When pgAdmin 4 is opened it will ask for a password, please type out the password that you made while doing the setup for installing PostgreSQL. 
4. After that click on Server(1) tab on the left hand side and it will ask for the same password again, please enter it again. On default, you will have a database called postgres already installed, you can use this database, but we would recommend you to make a new database and name it homicide_news.
5. To make a new database called homicide_main then click on Database(1), the right click on it, click on create --> Database..
6. A Create - Database menu will pop up in which in the first input box, please type in homicide_main.
7. Right now you should have a Database called homicide_main created in pgAdmin 4 which has no tables in it 

Next please follow the instructions given on the ConnectionReadme.txt