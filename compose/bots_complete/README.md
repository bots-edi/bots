# The BOTS "Complete" Dockerfile

## Introduction 
This dockerized version should provide a quick installable version of BOTS that runs "out of the box". 

The file contains a dockerized version with all optional functionalities activated in BOTS: 

1. Web-Server (default)
2. Directory Monitor
3. Job-Queue 

In addition, following tools are used to control the environment: 

1. Supervisor to manage start up services 
2. Devcron to manage cron-like jobs


## Docker Compose File
The docker compose file stored at the root of this repo, may be used to create the instance of BOTS by issueing: 

	docker-compose -f complete.yaml up 
	

Docker will then build BOTS based on Ubuntu 16:04 and Python 2.7. 
Supervisor's http log-in can be password protected through environment variables, here defined as SUPERVUSER and SUPERVPASS. 

Port 8080 is used to provide BOTS Web interface
Port 9001 is used for Supervisor HTTP interface

	version: '2'
	services:
  	  bots-complete:
  	    build:
          context: .
          dockerfile: ./compose/bots_complete/Dockerfile
        ports:
          - "0.0.0.0:8080:8080"
          - "0.0.0.0:9001:9001"
        environment:
          - SUPERVUSER=bots
          - SUPERVPASS=botsbots
        command: /usr/local/bin/supervisord -c /etc/supervisor/supervisord.conf	
After the build, one can connect to the terminal as follows: 

	docker exec -i -t bots_bots-complete_1 /bin/bash

To share local direcotires with the dockerized BOTS instance, add following to the corresponding entries (example below)docker-compose file. 

	volumes:
      - ./config:/usr/local/lib/python2.7/dist-packages/bots/config
      - ./botssys:/usr/local/lib/python2.7/dist-packages/bots/botssys
      - ./usersys:/usr/local/lib/python2.7/dist-packages/bots/usersys


	
## The postinstall file
The postinstall changes the default bots.ini to enable: 
- job-queue 
- map directory monitor to /dirmon directory. To make real use of that, the postinstall file should be amended to provide a route that is called when a file is stored. Currently the route argument remains empty. 


## Supervisord 
Startup definitions are defined in the supervisord file. 
Read more here: [Supervisord.org](http://supervisord.org)


## crontab
The crontab file is copied to the bots/config directory from where the dev-cron is started. When the file is changed, the service may require to be restarted to get the updates (untested..., but definitly if the host is shared from the host). 
Read more here: [DevCron](https://bitbucket.org/dbenamy/devcron/overview)
