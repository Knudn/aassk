# AASSK (Åseral snøscooterklubb) Digital signage ++

### Context
##### The purpose of this project is to automate the distrobution of images that will be used for Digital Signage.

This system should in theory be stateless which means very little manual configureration should be necessary. 

Since this software was written to operate in a segmented local network with no additional guests, very little security was considered! DO NOT DEPLOY THIS ON A PUBLIC NETWORK! 

This software suite will do the following things:
- Setup an SMB fileshare
- Setup the slideshow application
- Initiate the clients

#### Folder Struture:

##### slide_app
A Flask application used to display the images being put in the SMB file share. 
Ref: https://github.com/Digital-Signage-Slideshow/DS_Slideshow
##### tools
Contains all the custom deployment tools
### Prerequisite

This software was writter to be compateble with Debian on ARM, it should technically work on x86 but this cannot be guaranteed.

#### Controller
This act as the main hub which will orcestrate all the services used (db, Flask, smb, etc..).
The deployment tools are written for Debian on ARM, but most of the script should work with other distributions/architectures as well after a bit of tinkering

#### Client
The client needs to have Chromium installed, and needs to be manageable by SSH with the user root (security was not considered when designing this). 
As long as the controller has enough resources, any amount of clients can be deployed.

### Setup - Controller

1. Clone the repo
`git clone https://github.com/Knudn/aassk.git; cd aassk/tools`
2. Open instances.yaml to configure the clients
2. Install the SMB share
`chmod +x smb_share.sh; ./smb_share.sh --install`

3. Deploys the webserver, one for each client
`chmod +x setup_slide.sh; ./setup_slide.sh`


