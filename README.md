# Connectivity Manager Agent for usage with Open vSwitch

This tool exposes an REST API to a local Open vSwitch. In this case it was used in an environment with OpenStack and a corresponding Connectivity Manager that is part of an orchestration tool.

## Installation
Compile and Install the Connectivity Manager Agent:

`./cm-agent.sh install`

This command checks that all the dependencies are installed on the host machine (i.e. git, python-pip, setuptools) and installs all the required Python packages (using pip) in a virtual environment.
After doing that the source code is compiled and installed to /opt/cm/cm-agent.


## Initialization and configuration

After the installation the config file needs to be updated to reflect the correct OpenStack credentials:

`./cm-agent.sh init`

This command sets the username and password for the usage of the OpenStack environment. Else it can be edited manually in `/etc/cm/cm-agent/cm-agent.properties`

Make sure all Hosts within the tenant have opened the port 6640 for accessing the OVSDB via port and run the following command to allow it to be accessed remotely:

`sudo ovs-vsctl set-manager ptcp:6640`

## Usage
Manually start a screen session (it can't be started automatically without further configuration because of the use of virtualenv's):

`screen -m -d -S cm-agent`

Now within the screen session the CM Agent can be started:

`./cm-agent.sh start`

The API of the CM Agent is now served on *Port 8091*.
