# AASSK (Åseral snøscooterklubb) Digital signage ++

### Context
##### The purpose of this project is to automate the distrobution of images that will be used for Digital Signage.

This system should in theory be stateless which means very little manual configureration should be necessary. 

Since this software was written to operate in a segmented local network with no additional guests, very little security was considered! DO NOT DEPLOY THIS ON A PUBLIC NETWORK! 

This software suite will do the following things:
- Setup an SMB fileshare
- Setup the slideshow application
- Initiate the clients

#### Struture:

##### slide_app


### Prerequisite

This software was writter to be compateble with Debian on ARM, it should techiclly workd on x86 put this cannot be guaranteed.

1 Controller: This act as the main hub which will run all the microservices.

### Setup


1. Clone the repo
`git clone https://github.com/Knudn/aassk.git`
2. 



