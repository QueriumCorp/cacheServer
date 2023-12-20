# cacheServer

# Set up Ubuntu Service 

## Requirements
- python 3.10 or higher

To check the python version
```
python3 --version
```

## Installation
Change to a directory you want to keep cacheServer
```
cd /home/webappuser/evan/repos/
```
Clone the github repository 
```
git@github.com:QueriumCorp/cacheServer.git
```
Change to the repository
```
cd cacheServer
```
Create a virtual environment for the repository
```
python3 -m venv .venv
```
Activate the virtual environment
```
source .venv/bin/activate
```
Check for installed packages
```
pip list
```
Install all required packages
```
pip install -r requirements.txt
```
Check for installed packages. You should see more packages now
```
pip list
```
Create a symbolic link to the program in the repository
```
sudo ln -s /home/webappuser/evan/repos/cacheServer/main.py /usr/local/bin/cacheServer
```
Copy the unit configuration file to the systemd directory
```
sudo cp /home/webappuser/evan/repos/cacheServer/cacheServer.service /etc/systemd/system/cacheServer.service
```
Update the values of User, WorkingDirectory, and ExecStart in cacheServer.service
```
sudo vi /etc/systemd/system/cacheServer.service
- - - the file content - - -
[Unit]
Description=Systemd service that schedules test-paths based on a test-schedule.

[Service]
Type=simple
User=webappuser
WorkingDirectory=/home/webappuser/evan/repos/cacheServer
Environment="DISPLAY=:1"
ExecStart=/home/webappuser/evan/repos/cacheServer/.venv/bin/python /usr/local/bin/cacheServer
Restart=always

[Install]
WantedBy=multi-user.target
```
Reload systemd manager configuration 
```
sudo systemctl daemon-reload
```
Helpful systemctl commands
```
sudo systemctl status cacheServer
sudo systemctl restart cacheServer
journalctl -u cacheServer
```

## Troubleshoot
If you are running a clean python3, you may not have the venv package. This package enables you to set up an isolated environment for each project. To install it, you can run the following command.
```
sudo apt install python3.10-venv
```