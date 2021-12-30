#!/usr/bin/env python

# python imports
from falconpy.hosts import Hosts
from falconpy.oauth2 import OAuth2
from falconpy.api_complete import APIHarness
import json
import logging
import sys

# local imports
from Send2HumioHEC import Send_to_HEC as humio
import CrowdStrikeDevices2HumioConfig as config


def main():
    clientID = config.CS_devices_client_id
    secret = config.CS_devices_client_secret
    log_file = config.log_file
    version = config.CS_devices_version
    log_level = config.CS_devices_log_level
    proxy_used = config.CS_devices_proxy
    proxies = config.CS_devices_proxies

    logging.basicConfig(filename=log_file, filemode='a+',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level)
    logging.info('Devices2Humio v' + version + ': CrowdStrike Devices to Humio is starting')

    if proxy_used == False:
        falcon = APIHarness(client_id=clientID, client_secret=secret)
    elif proxy_used == True:
        falcon = APIHarness(client_id=clientID, client_secret=secret, proxy=proxies)

    kwargs = {'clientID': clientID, 'secret': secret, 'falcon': falcon, 'log_file': log_file,
              'log_level': log_level, 'version': version, 'proxy': proxy_used, 'proxies': proxies}
    process_list = get_device_ids(**kwargs)
    kwargs['process_list'] = process_list
    logging.info('Devices2Humio v' + version + ': Getting device details')
    device_details = get_device_details(**kwargs)
    num_devices = len(device_details)

    for details in device_details:
        details_str = "\n".join(map(str, details))
        details_str = details_str.replace("True", "true")
        details_str = details_str.replace("False", "false")
        details_str = details_str.replace("None", "[]")
        details_str = details_str.replace("null", "[]")
        details_str = details_str.replace("'", '"')

        details_raw = json.dumps(details_str)
        details_json = json.loads(details_raw)

        logging.info('Devices2Humio v' + version + ': Sending details about ' + str(num_devices) + ' devices to Humio HEC')
        humio.send_to_HEC(details_json, num_devices)

        try:
            sys.exit('Devices2Humio v' + version +
                     ': Data collection has successfully completed, CrowdStrike Device Data 2 Humio is now exiting.')
        except:
            pass


def authentication(**kwargs):
    clientID = kwargs.get('clientID')
    secret = kwargs.get('secret')
    falcon = kwargs.get('falcon')
    version = kwargs.get('version')
    log_file = kwargs.get('log_file')
    log_level = kwargs.get('log_level')

    logging.basicConfig(filename=log_file, filemode='a+',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level)

    payload = {"client_id": clientID, "client_secret": secret}
    logging.info('Devices2Humio v' + version + ': Attempting to retrieve OAuth2 token from CrowdStrike')
    try:
        response = falcon.command("oauth2AccessToken", data=payload)
        access_token = (response['body']['access_token'])
    except Exception as e:
        logging.error('Devices2Humio v' + version + ': Unable to collect device data from CrowdStrike ' + e.message + '  ' + e.args)
        sys.exit('Devices2Humio v' + version + ' : Please correct any issues and try again - Devices2Humio will now exit')

    return access_token


def get_device_ids(**kwargs):
    falcon = kwargs.get('falcon')
    device_ids = []
    process_list = []

    PARAMS = config.PARAMS

    response = falcon.command("QueryDevicesByFilter", parameters=PARAMS)
    pagination = response['body']['meta']['pagination']

    total_id = pagination['total']
    offset = pagination['offset']
    response_ids = response['body']['resources']
    for id in response_ids:
        device_ids.append(id)
    remaining_ids = total_id - offset
    if remaining_ids > 0:
        paginate = True
    else:
        paginate = False

    while paginate == True:
        if remaining_ids > 0:
            PARAMS["offset"] = offset
        else:
            PARAMS["offset"] = offset
            paginate = False
        response = falcon.command("QueryDevicesByFilter", parameters=PARAMS)
        pagination = response['body']['meta']['pagination']
        total_id = pagination['total']
        offset = pagination['offset']
        remaining_ids = total_id - offset
        response_ids = response['body']['resources']
        for id in response_ids:
            device_ids.append(id)
    process_len = len(device_ids)

    while process_len > 0:
        print("Process list length: " + str(process_len))
        if process_len >= 400:
            process_ids = device_ids[0:400]
            process_list.append(process_ids)
            del device_ids[0:400]
            process_len = len(device_ids)
        else:
            process_len = len(device_ids)
            print('Remaining number of IDs: ' + str(process_len))
            if process_len == 0:
                pass
            elif process_len == 1:
                process_ids = device_ids.copy()
                print('Len process_ids: ' + str(len(process_ids)))
                process_list.append(process_ids)
                process_ids = device_ids
                del device_ids[0]
            else:
                process_ids = device_ids.copy()
                process_list.append(process_ids)
                del device_ids[::]
        process_len = len(device_ids)

    return process_list


def get_device_details(**kwargs):
    falcon = kwargs.get('falcon')
    process_list = kwargs.get('process_list')
    device_details = []

    for id_list in process_list:
        response = falcon.command("GetDeviceDetails", ids=id_list)
        detail_info = response['body']['resources']
        print('Details for ' + str(len(detail_info)) + ' devices will be added.')

        device_details.append(detail_info)

    return device_details  # device_info_1 #


if __name__ == "__main__":
    main()
