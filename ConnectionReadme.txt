Good Day
This is the ConnectionReadme file in which instructions to establish a connection between homicide_main database and python file called main.py will be explained.
Before continuing with the instruction on this read me, please ensure that you have completed the instructions given to you in ServerReadme.txt

Connection Setup Instructions:
1. Open the database.ini file in VS code
2. Change the password to the password that you have set when installing and setting up PostgreSQL.
3. If you are using the database called homicide_main, then you can close the file. If not then change the homicide_main written after database = to whatever your database name is
4. Please open the main.py file -- The main.py file is used to create a two tables one is called open_day_homicide_data and the other is called homicide_news - you can delete one of the table if you want to 
5. Go to line 173, there change the csv_file_path to the directory where you have stored the CSV file which has the homicide data that you want to input into the table
6. Go to line 176, and then change the variable called open_day_csv_file_path and put in the file directory where you have stored the CSV file which has at the homicide data that you want to input in to the table
7. You can now run the main.py file by pressing run python file on VS code and it will create two tables one called homicide_news and the other open_day_homicide_data
8. To check if these two tables are made, please go to pgAdmin 4 
9. Click on homicide_main or the database you are using for homicide media analysis tool, then right click it and then click on Query Tool. This will open the query for the database 
10. In the Query Tool, type "SELECT * FROM homicide_news;" without the quotation mark and execute the query by pressing the triangle run button or the shortcut F5
11. This will allow you to see the table called homicide_news and the fields in it.
12. Then to check the open_day_homicide_data table, in the Query Tool type "SELECT * FROM open_day_homicide_data;" without the quotation marks. 
13. Highlight SELECT * FROM open_day_homicide_data; and then press run or F5 to execute the query which will allow to see the table called open_day_homicide_data and check the fields in it.

IMPORTANT NOTES:
1. Please note that the field name in the CSV file that you will input in to the table must match the field names of the table or else you will get an error
2. To check the field name in each table please look at the function called create_homicide_news_table(cursor) for homicide_news table and create_open_day_homicide_table(cursor) for the 
open_day_homicide_data table.
3. You can change the field names in the table but make sure to change the corresponding field name in function that inputs the data from the CSV file into the table. The name of the functions that input the data from the CSV file into the table is called copy_from_csv(cursor, csv_file_path) for the homicide_news table copy_from_open_day_csv(cursor, csv_file_path) for the open_day_homicide_data table.

You have now established a connection between the main.py file and the database as well as created two tables. Now please follow the steps in the DashboardReadme.txt