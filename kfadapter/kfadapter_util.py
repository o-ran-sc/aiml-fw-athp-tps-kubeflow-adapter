# ==================================================================================
#
#       Copyright (c) 2022 Samsung Electronics Co., Ltd. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ==================================================================================
"""kfadapter_util.py.

This module is for all the utility functions to be used
by the main and other modules

"""

import traceback
import string
import time
import json
import requests
from random import choices

from flask_api import status

from kfadapter import kfadapter_conf

class BadRequest(Exception):
    """
    This is a class for throwing custom exception  when local error occurs

    Attributes:
        message: Custom message for the exception occured
        status: Error code for the exception
        payload: Custom payload for diagnostic purpose
    """
    def __init__(self, message, sts_code=status.HTTP_400_BAD_REQUEST, payload=None):
        """
        The constructor for BadRequest class.

        Parameters:
            message: Custom message for the exception occured
            status: Error code for the exception
            payload: Custom payload for diagnostic purpose
         """
        super().__init__()
        self.message = message
        self.status = sts_code
        self.payload = payload

def keys_match(dict1, dict2) -> bool:
    """
    check all keys from dict2 are present in dict1 or not
    """
    for key in dict2.keys():
        if key not in dict1:
            return False
    return True

def run_finished(run_status: string) -> bool:
    """
        Function for letting the caller know if run has finished
        based on run_status string reported from KubeFlow

        Args:
            run_status: status returned for run from KubeFlow

        Returns:
            true or false to signify whether run is finished or not

    """
    return run_status in {'SUCCEEDED', 'FAILED', 'ERROR', 'SKIPPED', 'TERMINATED'}

def random_suffix():
    """
        Function for generating random suffix

        Args: None

        Returns: random suffix

    """
    return ''.join(choices(string.ascii_lowercase + string.digits, k=10))

def wait_status_thread(name, kfc_kfconnect):
    """
     Thread Function for notify the status of all pipeline run
    to training manager

    Args:
        kfc_config: KfAdapter_config object

    Returns:None

    """
    #pylint: disable=unused-argument
    #pylint: disable=maybe-no-member
    kfc_config = kfadapter_conf.KfConfiguration.get_instance()
    logger = kfc_config.logger
    while True:
        with kfadapter_conf.LOCK:
            dict_copy = kfadapter_conf.TRAINING_DICT.copy()
            for i in dict_copy:
                try:
                    run = kfc_kfconnect.get_kf_run(i)
                    run_status = run.run.status
                except: # pylint: disable=bare-except
                    run_status = "Manual reconcile"

                if run_finished(run_status) or run_status == "Manual reconcile":
                    run_dict = {}
                    run_dict['run_id'] = i
                    run_dict['run_status'] = run_status
                    run_dict['trainingjob_name'] = kfadapter_conf.TRAINING_DICT[i]
                    logger.info("POSTING to training manager")
                    logger.info(run_dict)
                    payload = json.dumps(run_dict)
                    url = "http://"+kfc_config.trainingmgr_dict['trainingmgr_host']+":"+\
                                kfc_config.trainingmgr_dict['trainingmgr_port']\
                                + "/trainingjob/pipelineNotification"
                    logger.debug(url)
                    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
                    try:
                        response = requests.post(url, data=payload, headers=headers)
                        logger.info(response.json)
                    except requests.exceptions.ConnectionError as warn:
                        logger.warning("REST Server not running at %s", url)
                        logger.warning(warn)
                    except: # pylint: disable=bare-except
                        tbk = traceback.format_exc()
                        logger.error(tbk)
                    del kfadapter_conf.TRAINING_DICT[i]
                    break
                time.sleep(1)
        time.sleep(kfc_config.run_status_polling_interval_sec)

def check_list(data, compare_key):
    '''
    check compare_key presents in inner list or dictionary and return value for given compare_key
    '''
    for value in data:
        if isinstance(value, dict):
            ret = check_map(value, compare_key)
            if ret:
                return ret
        elif isinstance(value, list):
            ret = check_list(value, compare_key)
            if ret:
                return ret
        else:
            pass
    return None

def check_map(data, compare_key):
    '''
    check compare_key presents in inner list or dictionary or current dictionary and return value
    for given compare_key
    '''
    for key, value in data.items():
        if key == compare_key:
            return value
        if isinstance(value, dict):
            ret = check_map(value, compare_key)
            if ret:
                return ret
        elif isinstance(value, list):
            ret = check_list(value, compare_key)
            if ret:
                return ret
    return None
