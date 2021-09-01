#!/usr/bin/bash

function trap_ctrlc ()
{
    # perform cleanup here
    echo "Ctrl-C caught...performing clean up"
    rm temp
    
    exit 2
}

trap "trap_ctrlc" 2


ip_scan() { 
    ip=$(ping -c 1 -W 3 $1.$2 |grep "64 bytes" |cut -d " " -f 4|sed s/:// ) &>/dev/null
    if [ "$ip" != "" ]
    then
        echo $ip >>temp
    fi
    }

mac_scan(){
field=$(arp $1|grep -E "([0-9]{1,3}[\.]){3}[0-9]{1,3}")
if [ "$field" != "" ] && [[ "$field" != *"no entry"* ]]
then
ip=$(echo "$field"|grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}")
mac=$(echo "$field"|grep -E -o "..:..:..:..:..:..")

echo \""$ip\"":\""$mac\"",
fi
}

run()
# check if the user entered the subnet otherwise exit
if [ "$1" == "" ]
then
    echo "[-] missing arguments you must enter a subnet"
    exit
fi

# perform ip scan
for ip_end in {1..254..1}
do
    ip_scan $1 $ip_end &
done



wait
array=()
for i in $(cat temp)
do
array+=("$i")
done
rm temp


save_json(){
{
index=1

echo "{"
for i in "${array[@]} "
do  
    
    if [ $index -eq ${#array[@]} ]
    then
    mac_scan $i|sed s/,//
    else
    mac_scan $i
    fi
    ((index++))
done

wait
echo "}"
}>data.json

echo "[+] saved output to json"
}

save_json

exit 0