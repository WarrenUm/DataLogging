# DataLogging
I am using the Freematics One as a datalogger. In this project, I manipulate the data to make it more useable. Then, I will explore further what I can do with it.

The Arduino supplies the following code:value pairs from my car:

- 0x104 – Engine load
- 0x10c – Engine RPM
- 0x10d – Vehicle speed
- 0x111 – Throttle position
- 0x11 – UTC Date (DDMMYY)
- 0x10 – UTC Time (HHMMSSmm)
- 0xA – Latitude
- 0xB – Longitude
- 0xC – Altitude (m)
- 0xD – Speed (km/h)
- 0xF – Number of satellites in use
- 0x20 – Accelerometer data (x:y:z)
- 0x24 – Battery voltage (in 0.01V)

They are stored in a csv, but I had to pick out the data using the codes and make new dataframes.

The Data_Cleaning_Exploration notebook was the first notebook. In it, I go though how I organize the data into different tables. The data comes from the Arduino as code:value pairs that needed to be placed into different columns. I separated accelerometer data from the rest because I go that data four times as often as the rest. Then, I split up what was left based on if it came from the vehicle computer or the gps.

After that, I changed data types and converted units. The vehicle computer data units are corrent, but the gps speed still needs to be fixed. I also changed the indices to a datetime format. I finished by saving the new data in its own folder with the date and time that the trip started.

Tables Saved:

  Accelerometer
 - 0x20 – Accelerometer data (x:y:z)
 
  GPS Data
 - 0x11 – UTC Date (DDMMYY)
 - 0x10 – UTC Time (HHMMSSmm)
 - 0xA – Latitude
 - 0xB – Longitude
 - 0xC – Altitude (m)
 - 0xD – Speed (km/h)
 - 0xF – Number of satellites in use
 
 Vehicle Data
 - 0x104 – Engine load
 - 0x10c – Engine RPM
 - 0x10d – Vehicle speed
 - 0x111 – Throttle position
 - 0x24 – Battery voltage (in 0.01V)

In the file_processing notebook, I ironed out how I would process all of the data files and made fuctions for each step.
I saved the functions to a python file.

The notebook, Process_all_files, is where I process each file and place them in their own folders named using the date and time of the trip. This data is stored in the Converted folder without location information so that I can upload it to GitHub.

I started making a trip class in the trip_classes notebook. Currently, each trip contains basic stats like the starting and ending time of the trip, speed stats, and max engine rpm information. There are three functions in the trip class. The first prints the duration, average speed, and max speed for the trip. The second and third functions get the starting and ending locations using reverse_geocoder. They do not work using the data uploaded to GitHub because the latitude and longitude were removed.
