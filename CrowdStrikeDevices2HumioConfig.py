#!/usr/bin/env python

#python imports
import logging
import datetime
from datetime import timedelta

#Set Logging level and file name
CS_devices_log_level = logging.DEBUG
log_file = 'CrowdStrikeDevices2Humio.log'

#Code version - do not alter
CS_devices_version = '1.0'

#Proxy config
CS_devices_proxy = False
CS_devices_proxies = {}
#Example of Proxy syntex {"http": "http://myproxy:8888", "https": "https://myotherproxy:8080"}

#####CrowdStrike Devices Configuration

#use a timedelta to create a time in the past to populate the 'last_seen' filter
current_time = datetime.datetime.now()
look_back = current_time - timedelta(hours=2)
last_seen = look_back.strftime("%Y-%m-%dT%H:%M:%SZ")

#CrowdStrike API Filters
PARAMS = {'limit':2000, 'filter':"last_seen:>'" + last_seen +"'"}

#CS_devices_limit = 
#CS_devices_filter = "&filter=last_seen:>'2021-10-05T00:00:12Z'" #Time may be configured but needs to remain in single quotation marks

#CrowdStrike API credential with Devices Scope
CS_devices_client_id=""
CS_devices_client_secret=""

#The base URL for CrowdStrike cloud to connect to, this URL can be found in the Falcon UI on the API client page
CS_devices_base_url = 'https://api.crowdstrike.com'

#CrowdStrike API endpoints 
CS_devices_tokenURL = "/oauth2/token"
CS_devices_scroll_url = "/devices/queries/devices-scroll/v1"
CS_devices_url = "/devices/entities/devices/v1?"

#####Humio HEC configuration

#Humio URL
HumioBaseURL = ''
HumioHECurl = HumioBaseURL+'/api/v1/ingest/hec/raw'  
#example of a full URL: http://192.168.0.220:8080/api/v1/ingest/hec/raw


#Humio HEC Token
HumioHECtoken_Devices = ''

#Header Content Type
HumioHECcontent_Devices  = "'application/json', 'Accept':'application/json'"

#Certficate validation - should only be set to false in a controlled test environment 
HumioHECverify = True






