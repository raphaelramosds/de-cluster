#!/bin/bash
# ██████╗  ██████╗ █████╗
# ██╔══██╗██╔════╝██╔══██╗
# ██║  ██║██║     ███████║
# ██║  ██║██║     ██╔══██║
# ██████╔╝╚██████╗██║  ██║
# ╚═════╝  ╚═════╝╚═╝  ╚═╝
# DEPARTAMENTO DE ENGENHARIA DE COMPUTACAO E AUTOMACAO
# UNIVERSIDADE FEDERAL DO RIO GRANDE DO NORTE, NATAL/RN
#
# (C) 2022-2025 CARLOS M D VIEGAS
# https://github.com/cmdviegas
#

### Description:
# This is a bash script to initialize services

### How it works:
# On first startup:
# - Load .bashrc
# - Start SSH server
# - Format namenode HDFS (spark-master only)
# - Creates HDFS folders and copy files to them (spark-master only)
# - Edit HADOOP/SPARK properties in .xml/.conf files according to values defined in .env
# - Start HDFS, YARN and SPARK HISTORY SERVER

# In the next startups:
# - Load .bashrc
# - Start SSH server
# - Edit HADDOP/SPARK properties in .xml/.conf files according to values defined in .env
# - Start HDFS, YARN and SPARK HISTORY SERVER

# Some coloring
RED_COLOR=$(tput setaf 1)
GREEN_COLOR=$(tput setaf 2) 
YELLOW_COLOR=$(tput setaf 3)
LIGHTBLUE_COLOR=$(tput setaf 6)
RESET_COLORS=$(tput sgr0)
INFO="[${GREEN_COLOR}INFO${RESET_COLORS}]${LIGHTBLUE_COLOR}"
WARN="[${RED_COLOR}ERROR${RESET_COLORS}]${YELLOW_COLOR}"

###
#### Load env variables
[ -f "${HOME}/.env" ] && . "${HOME}/.env"
###

###
#### .bashrc
# Load .bashrc
eval "$(tail -n +10 ${HOME}/.bashrc)" # Workaround for ubuntu .bashrc (i.e. source .bashrc)
###

###
#### Run script to update .xml config of hadoop and spark
[ -f "${HOME}/config-xml.sh" ] && bash -c "${HOME}/config-xml.sh"
###

###
#### Init ssh server
sudo service ssh start
###

###
#### /etc/hosts and ~/hadoop/etc/hadoop/workers
# Creates /etc/hosts dynamically according to number of replicas and update hadoop workers file accordingly
truncate -s 0 ${HADOOP_CONF_DIR}/workers
{
    echo "127.0.0.1 localhost"
    echo "${IP_MASTER} ${MASTER_HOSTNAME}"
    for i in $(seq 1 "${REPLICAS}"); do
        echo "${IP_RANGE%0/*}$((i+2)) worker-$i"
        echo "worker-$i" >> "${HADOOP_CONF_DIR}/workers"
    done
} | sudo tee /etc/hosts > /dev/null # Copy hosts file to /etc/hosts
###

###
#### Init services
# Initialize hadoop services (only at spark-master)
if [ "$1" == "MASTER" ] ; then

    # Format HDFS
    printf "${INFO} Formatting filesystem${RESET_COLORS}...\n"
    hdfs namenode -format -nonInteractive

    # Start HDFS and YARN services
    # Test if all workers are alive and ready to create the cluster
    ATTEMPTS=0
    while true
    do
        printf "${INFO} Waiting for WORKERS to be ready${RESET_COLORS}...\n"
        WORKERS_REACHABLE=true
        # Read the file containing the IP addresses
        while IFS= read -r ip; do
            if ! ssh -o "ConnectTimeout=1" "$ip" exit >/dev/null 2>&1; then
                # If any worker node is not reachable, set WORKERS_REACHABLE to false and break the loop
                WORKERS_REACHABLE=false
                break
            fi
        done < ${HADOOP_CONF_DIR}/workers
        if ${WORKERS_REACHABLE}; then
            # If all worker nodes are reachable, start hdfs and yarn and exit the loop
            printf "${INFO} Starting HDFS and YARN services${RESET_COLORS}...\n"
            sleep 1
            start-dfs.sh && start-yarn.sh
            break
        fi
        # Wait before checking again
        sleep 5

        ATTEMPTS=$((ATTEMPTS+1))
        if [ ${ATTEMPTS} -ge 10 ]; then
            printf "${WARN} There are no reachable WORKERS. Exiting.${RESET_COLORS}\n"
            exit 1
        fi
    done

    sleep 1

    # Creating /user folders inside HDFS
    if ! hdfs dfs -test -d "/user/${HDFS_NAMENODE_USER}"; then
        # Check if there are live datanodes in the cluster
        if hdfs dfsadmin -report | grep -q "Live datanodes"; then
            printf "${INFO} Creating folders in HDFS${RESET_COLORS}...\n"
            hdfs dfs -mkdir -p "/user/${HDFS_NAMENODE_USER}" /spark-logs /spark-libs
            printf "${INFO} Copying spark libs to HDFS${RESET_COLORS}...\n"
            hdfs dfs -put "${SPARK_HOME}/jars/"*.jar /spark-libs/
        else
            printf "${WARN} There are no live nodes in the cluster. Exiting.${RESET_COLORS}\n"
            exit 1
        fi
    fi
    
    # Starting SPARK history server
    printf "${INFO} Starting SPARK history server${RESET_COLORS}...\n"
    start-history-server.sh

    # Checking HDFS status (optional)
    printf "${INFO} Checking HDFS nodes report${RESET_COLORS}...\n"
    hdfs dfsadmin -report

    # Checking YARN status (optional)
    printf "${INFO} Checking YARN nodes list${RESET_COLORS}...\n"
    yarn node -list

    printf "${INFO} Creating Kafka logs\n"
    kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c $KAFKA_HOME/config/kraft/server.properties

    printf "${INFO} Starting Kafka server\n"
    kafka-server-start.sh $KAFKA_HOME/config/kraft/server.properties &
    sleep 5

    printf "${INFO} Starting Spark Connect server\n"
    start-connect-server.sh --packages org.apache.spark:spark-connect_2.12:3.5.4,org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2 &
    sleep 5

    printf "${INFO} Starting Kafka Connect\n"
    connect-standalone.sh $KAFKA_HOME/config/connect-standalone.properties &
    sleep 5

    printf "\n${INFO} ${GREEN_COLOR}$(tput blink)ALL SET!${RESET_COLORS}\n\n"
    printf "TIP: To access ${MASTER_HOSTNAME}, type: ${YELLOW_COLOR}docker exec -it ${MASTER_HOSTNAME} /bin/bash${RESET_COLORS}\n"
fi
# Starting bash terminal
/bin/bash

[ "$1" == "WORKER" ] && printf "${INFO} I'm up and ready${RESET_COLORS}!\n"

unset USER_NAME
unset PASSWORD
