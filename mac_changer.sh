#!/usr/bin/bash

if [ "$EUID" != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi


function changeMacAdress()
{
ifconfig "$1" down
while true
do
read -p "Enter new mac address : " newmac
if [[ "$newmac" =~ ^([[:xdigit:]]{2}[:.-]?){5}[[:xdigit:]]{2}$ ]]
then
  ifconfig "$1" hw ether "$newmac"
  if [ ! $? -eq 0 ]
  then
    echo "[-] valid address but cannot assign it"
  else
    ifconfig "$1" up
    break;
  fi
else
  echo "[-] invalid mac address"
fi
done

echo "[+] changing MAC address ..."



ifconfig "$1" up

macadress=$(ifconfig $(echo "$1" | xargs) | grep -e ..:..:..:..:..:.. | xargs | cut -d " " -f 2) &>/dev/null
if [ "$macadress" == "$newmac" ]
then
  echo "[+] successfully changed macaddress for interface : $1 to $newmac"
else
  echo "[-] error occured macaddress wasn't changed"
fi
}
interfaces=()
var=$(ifconfig | grep "flags" | cut -d " " -f 1 | sed 's/://')
for line in $var
do
  interfaces+=("$line")
done
echo "Please choose an interface to change MAC address for"
select interface in "${interfaces[@]}"
do

  if [[ ! " ${interfaces[*]} " =~ " ${interface} " ]]
  then
    echo "[-] You picked an interface that doesn't exist number must be between 1-${#interfaces[@]}"
    exit
  fi

  macadress=$(ifconfig $(echo "$interface" | xargs) | grep -e ..:..:..:..:..:.. | xargs | cut -d " " -f 2) &>/dev/null
  if [ "$macadress" != "" ]
  then
    echo " current mac address for interface $interface is: $macadress"
    while true; do
    read -p "Do you wish to change this mac adress [Y/n]? " yn
    case $yn in
        [Yy]* )
        changeMacAdress $interface ;exit;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done
  else
    echo "[-] no mac address found for interface : $interface"
    exit
  fi
done
