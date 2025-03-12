#!/bin/bash

source /scripts/02-common.sh

log_message "RUNNING" "04-install-mt5.sh"

# Check if MetaTrader 5 is installed
if [ -e "$mt5file" ]; then
    log_message "INFO" "File $mt5file already exists."
else
    log_message "INFO" "File $mt5file is not installed. Installing..."

    # Set Windows 10 mode in Wine and download and install MT5
    $wine_executable reg add "HKEY_CURRENT_USER\\Software\\Wine" /v Version /t REG_SZ /d "win10" /f
	if [ -e "$mt5setup_file" ]; then
		log_message "INFO" "Downloaded MT5"
	else
		log_message "INFO" "Downloading MT5 installer..."
		wget -O /tmp/mt5setup.exe $mt5setup_url > /dev/null 2>&1
	fi
	
    log_message "INFO" "Installing MetaTrader 5..."
    $wine_executable /tmp/mt5setup.exe /auto 
fi

# Recheck if MetaTrader 5 is installed
if [ -e "$mt5file" ]; then
    log_message "INFO" "File $mt5file is installed. Running MT5..."
    $wine_executable "$mt5file" &
#    rm -f /tmp/mt5setup.exe
else
    log_message "ERROR" "File $mt5file is not installed. MT5 cannot be run."
fi