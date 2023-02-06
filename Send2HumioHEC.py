#!/usr/bin/env python

# python imports
import requests
import logging
import sys

# local imports
import CrowdStrikeDevices2HumioConfig as config

class Send_to_HEC():

    def send_to_HEC(event_data, num_devices, group_num):
        HumioHECurl = config.HumioHECurl
        HumioHECcontent = config.HumioHECcontent_Devices
        HumioHECverify = config.HumioHECverify
        log_level = config.CS_devices_log_level
        proxy_used = config.CS_devices_proxy
        proxies = config.CS_devices_proxies

        version = config.CS_devices_version
        logging.basicConfig(filename=config.log_file, filemode='a+',
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level)
        logging.info('Devices2Humio v' + version + ':  HEC: Sending data to Humio HEC')

        try:
            header = {"Authorization": "Bearer " + config.HumioHECtoken_Devices, "Content-Type": HumioHECcontent}
            if proxy_used == False:
                r = requests.post(url=HumioHECurl, headers=header, data=event_data, 
                                  verify=HumioHECverify, timeout=300, )
                transmit_result = r.status_code
            elif proxy_used == True:
                r = requests.post(url=HumioHECurl, headers=header, data=event_data,
                                  verify=HumioHECverify, timeout=300, proxies=proxies)
                transmit_result = r.status_code

            logging.info('Devices2Humio v' + version + ':  HEC: Transmission status code for data push to HEC= ' + str(transmit_result))
            logging.debug('Devices2Humio v' + version + ':  HEC: Transmission device data for group ' + str(group_num ) + ' of ' + str(num_devices)
                           + ' to Humio HEC has successfully completed.')

        except (requests.exceptions.RequestException, UnicodeEncodeError) as e:
            error = str(e)
            logging.info('Devices2Humio v' + version + ':  HEC: Unable to evaluate and transmit sensor_data event: Error: ' + error)
            try:
                sys.exit('Devices2Humio v' + version +
                         ': HEC: This is fatal error, please review and correct the issue - CrowdStrike Intel Indicators to Humio is shutting down')
            except:
                pass

        return
