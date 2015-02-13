#!/bin/bash

CONFIG_DIR="/etc/nubomedia"
PROPERTIES_FILE="$CONFIG_DIR/cm-agent.properties"
SOURCE_CODE_DIR="cm-agent"
DEST="/opt/nubomedia"

function check_location {
  if [ ! -d "$SOURCE_CODE_DIR" ];
  then
    echo "Can not find folder $SOURCE_CODE_DIR. Please check from where you are starting this command. It should be executed directly in the folder where the emm.sh script is located." 1>&2
    exit 1
  fi
}

function check_root_privileges {
  if [[ $EUID -ne 0 ]]; 
  then
    echo "This option must be run as root." 1>&2
    exit 1
  fi
}

function check_no_root_privileges {
  if [[ $EUID -eq 0 ]]; 
  then
    echo "Run this option without root privileges." 1>&2
    exit 1
  fi
}

function create_config_dir {
  if [ -d "$CONFIG_DIR" ]; then
    echo "Found config dir $CONFIG_DIR"
  else
    echo "Creating config dir $CONFIG_DIR"
    mkdir "$CONFIG_DIR"
  fi
}

function copy_properties_file {
  cp cm-agent/cm-agent.properties $PROPERTIES_FILE 
}

function copy_source_code {
  if ! [ -d "$DEST" ]; then
    mkdir $DEST
  fi
  cp -r ./cm-agent /opt/nubomedia
}

function set_openstack_credentials {
  echo -n "os_tenant="
  read -r os_tenant_name
  echo -n "os_username="
  read -r os_username
  echo -n "os_password="
  read -r os_password
  echo -n "os_auth_url="
  read -r os_auth_url

  if [ -f "$PROPERTIES_FILE" ]; then
    if [ -n "$os_tenant_name" ]; then
      sed -i "s/\(os_tenant=\).*/\1$os_tenant_name/" "$PROPERTIES_FILE"
    fi
    if [ -n "$os_username" ]; then
      sed -i "s/\(os_username=\).*/\1$os_username/" "$PROPERTIES_FILE"
    fi
    if [ -n "$os_password" ]; then
      sed -i "s/\(os_password=\).*/\1$os_password/" "$PROPERTIES_FILE"
    fi
    if [ -n "$os_auth_url" ]; then
      sed -i "s/\(os_auth_url=\).*/\1${os_auth_url}/" "$PROPERTIES_FILE"
    fi
  else
    echo "ERROR: Cannot find $PROPERTIES_FILE"
    exit 1
  fi
}


function check_openstack_credentials {
  if [ -f "$PROPERTIES_FILE" ];
  then
    while read line
    do
      IFS='=' read -ra part <<<"$line"
      if ! ([ $part == "os_tenant" ] || [ $part == "os_username" ] || [ $part == "os_password" ] || [ $part == "os_auth_url" ]); then
        echo "No tenant name, username or password was set for Openstack. Run init first."
        exit 1
      fi
    done < "$PROPERTIES_FILE" 
  else 
    echo "No tenant name, username, password or auth_url was set for Openstack. Run init first."
    exit 1
  fi
}

function install_pip_requirements {
  cd "$SOURCE_CODE_DIR"
  venv/bin/pip install -r requirements.txt
  cd ..
}

function compile_and_install_server {
  cd "$SOURCE_CODE_DIR"
  venv/bin/python setup.py build
  venv/bin/python setup.py install
  venv/bin/python setup.py install
  cd ..
}

function uninstall_cmagent {
  cd "$SOURCE_CODE_DIR"
  venv/bin/python setup.py install --record ../files.txt
  cd ..
  cat files.txt | xargs rm -rf
  rm files.txt
  rm -rf "$CONFIG_DIR"
}

function is_pkg_installed {
  echo "Checking if $1 is installed"
  if [ $(dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
    echo "$1 is not installed"
    return 1
  else
    echo "$1 is installed"
    return 0
  fi
}

function update_pkgs {
  echo "Updating packages"
  apt-get update
  if [ "$?" ]; then
    echo "Updated packages successfully"
  else
    echo "ERROR: Cannot update packages"
    exit 1
  fi
}

function install_pkg {
  if ! is_pkg_installed "$1"; then
    echo "Installing $1"
    apt-get install --yes --force-yes "$1"
    if [ "$?" ]; then
      echo "$1 was installed successfully"
    else
      echo "ERROR: Cannot install $1"
      exit 1
    fi
  fi
}

function install_pip_pkg {
  if ! is_pip_pkg_installed "$1"; then
    echo "Installing $1"
    pip install $1 
    if [ "$?" ]; then
      echo "$1 was installed successfully"
    else
      echo "ERROR: Cannot install $1"
      exit 1
    fi
  fi
}

function is_pip_pkg_installed {
  echo "Checking if $1 is installed"
  if [ $(pip show "$1" 2>/dev/null | grep -c "Version:") -eq 0 ]; then
    echo "$1 is not installed"
    return 1
  else
    echo "$1 is installed"
    return 0
  fi
}

function check_requirements {
  echo "Checking if required Packages are installed"
  update_pkgs
  install_pkg git
  install_pkg python-pip
  install_pip_pkg virtualenv
}

function setup_virtualenv {
  echo "Setting up virtualenv"
  cd "$SOURCE_CODE_DIR"
  virtualenv venv
  cd ..
}

function start_cma {
  echo "For starting the Connectivity Manager in a screen session, manually create one first using 'screen -d -m -S cm-agent'"
  echo "and then rerun this command"
  cd "$SOURCE_CODE_DIR"
  venv/bin/python wsgi/application.py
}


###MAIN###

case "$1" in
install)
  check_root_privileges
  check_location
  check_requirements
  setup_virtualenv
  install_pip_requirements
  compile_and_install_server
  create_config_dir
  copy_properties_file
  copy_source_code
  ;;
init)
  check_root_privileges
  check_location
  set_openstack_credentials
  ;;
update) 
  check_root_privileges 
  check_location
  git pull
  compile_and_install_server
  ;;
start)  
  check_root_privileges 
  check_location
  start_cma

  ;;  
uninstall)
  check_root_privileges
  check_location
  uninstall_cmagent
  ;;
clean)  rm -rf build
  ;;
*)  echo "Usage: cm-agent.sh OPTION"
  echo "OPTION:"
  echo "  install   - install the server"
  echo "  update    - updates the server"
  echo "  start     - start the server"
  echo "  uninstall - uninstall the server"
  echo "  clean     - remove build files"
  ;;
esac


