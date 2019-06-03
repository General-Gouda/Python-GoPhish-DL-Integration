# Python-GoPhish-DL-Integration

Written By: Matt Marchese

Version: Beta - 2019.06.03

## **Summary**

- This program will pull a list of all groups within a local Active Directory and upload them into GoPhish for campaign usage.

## **Installation**

1. Extract files into a file folder on the host or server that will run the application.
2. Be sure Python 3 is installed on the system running the program (created and tested on v3.7.2).
    - This program has not been tested in Python 2.
3. Open a terminal, change the current working directory to where the application files are located and run `python3 -m pip install -r requirements.txt` to install required modules. On Windows run `python -m pip install -r requirements.txt` from Powershell or cmd (Be sure that Python is in your system's PATH).
4. Open the **Config.json.sample** file included in this repository and copy the contents to your clipboard. Create a new folder named **Config** at the root level (if one is not already there) and then create a new file within that new folder named **Config.json**. Paste the copied values into it. Modify the values with the proper information for your domain and GoPhish environment(s).
5. Create a new file in the root directory of the application named **app_pass** (no file extension) and place the password needed for accessing Active Directory by the username specified in **Config.json**.
6. Execute the *Start_Program.py* application by running `python3 ./Start_Program.py`, or `python .\Start_Program.py` on Windows, to begin the application.
    - The program begins an endless `while` loop that kicks off the main process once every 24 hours.

## **Container Notes**

- It is recommended that the *Config.json* file be inserted into a volume folder so that the config settings may be easily manipulated.
- It is recommended that the *Logs* folder be a volume so the log file will be available outide of the container.
- It is recommended that the *app_pass* file be inserted into a container as a Docker Secret or equivalent file directly into the file path of the program.

<!-- ## **Other Notes** -->
