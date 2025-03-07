# Homicide_media_tracker_tool
This is a homicide_media_tracker_tool that I made in my investigation project
GOOD DAY
This is the main Readme.txt in which we will discuss what is in the three folder that are presented. These three folders are related to the workings done for the project called 24P75 - Echoes of Crime: An open-source tool for homicide media analysis. Contents in the three folders are as follows:

1. Project_Dashboard_code: This folder/directory contains the dashboard for the homicide media analysis that is created using the Dash API/library in Python. This is the main dashboard that is created by both partners (Syed Anas and Muhammad Bux). This is also the dashboard that was shown in Open Day as our investigation project. The instruction to run the dashboard are present in the following Readme files: 
	1. ServerReadme.txt: In this Readme, the open-source required to run the dashboard are mentioned as well as their installation process. Moreover, the instructions to create the 	server side database is also mentioned. The instructions from this Readme need to be followed first to run the dashboard

	2. ConnectionReadme.txt: In this Readme, the instructions to establish a connection between the Python file main.py and the database in PostgreSQL is mentioned. Moreover, the 	instructions required to create a table in the database is also mentioned. The instructions from this Readme need to be followed second to run the dashboard.

	3. DashboardReadme.txt: In this Readme, the instructions required to run the dashboard.py file is mentioned which allow you to run the dashboard and use it for homicide media 	data collection, storage, analysis and visualisation. The instruction from this Readme file are the last instructions to follow to run the dashboard.


2. Project_Investigative_element: This folder/directory contains dashboard that was created and used for my investigation element in the project. My investigation element was to investigate which API would create a dashboard with very low complexity and that requires very low amount computer resources to run. For this reason another dashboard was created using the Streamlit API/library. This dashboard has the same functionality as the dashboard created using the Dash library. This is the secondary dashboard that was created by me (Syed Anas) for investigation element in the project and testing were done to see which dashboard from the two APIs is more complex and uses more computer resources to run. The instructions to run the dashboard are present in the following Readme files:
	1. ServerReadme.txt: In this Readme, the open-source required to run the dashboard are mentioned as well as their installation process. Moreover, the instructions to create the 	server side database is also mentioned. The instructions from this Readme need to be followed first to run the dashboard

	2. ConnectionReadme.txt: In this Readme, the instructions to establish a connection between the Python file main.py and the database in PostgreSQL is mentioned. Moreover, the 	instructions required to create a table in the database is also mentioned. The instructions from this Readme need to be followed second to run the dashboard.

	3. DashboardReadme.txt: In this Readme, the instructions required to run the dashboard.py file is mentioned which allow you to run the dashboard and use it for homicide media 	data collection, storage, analysis and visualisation. The instruction from this Readme file are the last instructions to follow to run the dashboard.


3. Project_Data: This folder/directory contains all the excel and CSV files that has homicide data which were used for development and testing of the homicide media analysis tool. There are two CSV file that are needed to run the code which are homicide_news_data.csv and Open_day_data.csv. Please remember where you have saved these two files and their file directory as it will be useful when trying to establish a connection between the dashboard and the database. The Readme file present in this folder shows what are the functions of each Excel and CSV files and where we got them from. 

IMPORTANT NOTES:
1. Please do not change the name of any functions in the code unless you know what you are doing. Changing the name of any function will result in breaking the code and the dashboard will not run.
2. When trying to run the Dash dashboard or the Streamlit dashboard, please first open the ServerReadme.txt file, and follow the instructions present in this file. After you are done, then you need to open the ConnectionReadme.txt file second and follow along with the instructions present in this file. Lastly, after you have executed in both the Readme files, please open the DashboardReadme.txt file and follow along with the instructions in this file to run the homicide media analysis tool.


