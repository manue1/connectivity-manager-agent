#!/bin/bash

config_dir="/etc/nubomedia"
user_file="$config_dir/user.cfg"
static_config_file="$config_dir/static_config.json"
static_template_file="$config_dir/nubo_templ.yaml"


function set_username_and_password {
	echo -n "username="
	read -r username
	echo -n "password="
	read -r password

	if [ -f "$user_file" ]
	then
		rm "$user_file"		
	fi
	echo "username=$username" >> $user_file
	echo "password=$password" >> $user_file
}

function check_username_and_password {
  if [ -f "$user_file" ];
  then
    while read line
    do
      IFS='=' read -ra part <<<"$line"
      echo $part
      if ! ([ $part[0] == "username" ] || [ $part[0] == "password" ]);
      then
        echo "No username or password. Run init first."
        exit 1
      fi
    done < "$user_file" 
  else 
    echo "No username and password. Run init first."
    exit 1
  fi
}

function check_root_privilegs {
	if [[ $EUID -ne 0 ]]; 
  then
    echo "This option must be run as root" 1>&2
	  exit 1
	fi
}

function set_config_files {
	if [ ! -d "$config_dir" ]
	then 
		mkdir $config_dir	
	fi
	cp "data/nubo_templ.yaml" "$config_dir"
	cp "data/static_config.json" "$config_dir"
}

function compile_and_install_server {
	python setup.py build
	python setup.py install
}
function uninstall_server {
	python setup.py install --record files.txt
	cat files.txt | xargs rm -rf
	rm -rf "$user_file" "$static_config_file" "$static_template_file"
}

function check_requirements {
	#echo "check that python-pip is installed"
	#if [ $(dpkg-query -W -f='${Status}' python-pip 2>/dev/null | grep -c "ok installed") -eq 0 ];
	#then
	#	echo "Updating packages"
  #  apt-get update
  #  echo "Installing python-pip"
	#	apt-get install python-pip;
	#	echo "python-pip was installed"
	#else
	#	echo "python-pip was already installed"
	#fi
	echo "check that python setuptools is installed"
	if [ $(pip show setuptools 2>/dev/null | grep -c "Version:") -eq 0 ];
	then
		echo "Installing python setuptools"
		easy_install setuptools
    #pip install setuptools
		echo "python setuptools was installed"
	else
		echo "python setuptools was already installed"
	fi 
}

###MAIN###

case "$1" in
install)
  check_root_privilegs
	check_requirements
	set_config_files	
	compile_and_install_server
	;;
init)
  set_username_and_password
  ;;
update)	
  check_root_privilegs 
	git pull
	set_config_files
	compile_and_install_server
	;;
start)	
  check_username_and_password
  python wsgi/application.py
	;;	
uninstall)
	check_root_privilegs
	uninstall_server
	;;
clean)	rm -rf build
	;;
*) 	echo "Usage: eem.sh OPTION"
	echo "OPTION:"
	echo "	install   - install the server"
	echo "	update 	  - updates the server"
	echo "	start 	  - start the server"
	echo "	uninstall - uninstall the server"
	echo "	clean 	  - remove build files"
	;;
esac

