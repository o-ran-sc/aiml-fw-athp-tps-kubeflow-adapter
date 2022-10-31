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
"""kfadapter_conf.py

This module is for retrieving configuration for KfAdapter App
Kubeflow configuration - Host ip, port, namespace
Application configuration - Application Port and run status interval


"""

from os import getenv
from threading import Lock

from .tmgr_logger import TMLogger

TRAINING_DICT = {}
LOCK = Lock()


class KfConfiguration:
    """
    This is a class for reading configuration for Kfadapter from
    environment variables.

    Attributes: None
    """

    __instance = None

    @staticmethod
    def get_instance():
        """
        create kfConfiguration instance if not created and return same object
        """
        if KfConfiguration.__instance is None:
            KfConfiguration()

        return KfConfiguration.__instance

    def __init__(self):
        """
        The constructor for KfConfiguration class.

        Parameters:None
         """
        if KfConfiguration.__instance:
            raise Exception("This class is a singleton!")
        KfConfiguration.__instance = self

        self.kf_dict = {}
        self.trainingmgr_dict = {}
        self.tmgr_logger = TMLogger("config/log_config.yaml")
        self.logger = self.tmgr_logger.logger

        self.run_status_polling_interval_sec = 20
        self.kf_dict['kfhostname'] = getenv('KUBEFLOW_HOST')
        self.kf_dict['kfport'] = getenv('KUBEFLOW_PORT')
        self.kf_dict['kfdefaultns'] = getenv('KF_NAMESPACE')
        self.appport = getenv('KF_ADAPTER_PORT')
        self.trainingmgr_dict['trainingmgr_host'] = getenv('TRAININGMGR_HOST') 
        self.trainingmgr_dict['trainingmgr_port'] = getenv('TRAININGMGR_PORT')

        
    @property
    def get_kflogger(self):
        """
        Function for giving logger instance to the caller of the function

        Args:None

        Returns:
            logger: returns logger instance

        """
        return self.logger

    def get_kfhostname(self):
        """
        Function for giving kfhostname to the caller of the function

        Args:None

        Returns:
            kfhostname: string revealing host ip or hostname where Kubeflow is hosted

        """
        self.logger.error("Getting hostname")
        return self.kf_dict['kfhostname']

    def get_kfport(self):
        """
        Function for giving kfport to the caller of the function

        Args:None

        Returns:
            kfport: string revealing port where Kubeflow sdk can connect

        """
        return self.kf_dict['kfport']

    def get_trainingmgrhost(self):
        """
        Function for giving trainingmgr_host to the caller of the function

        Args:None

        Returns:
            trainingmgr_host: string revealing host where trainingmgr can be contacted

        """
        return self.trainingmgr_dict['trainingmgr_host']

    def get_trainingmgrport(self):
        """
        Function for giving trainingmgr_port to the caller of the function

        Args:None

        Returns:
            trainingmgr_port: string revealing port where trainingmgr can be contacted

        """
        return self.trainingmgr_dict['trainingmgr_port']

    def get_kfnamespace(self):
        """
        Function for giving kfnamespace to the caller of the function

        Args:None

        Returns:
            kfnamespace: string revealing namespace in which pipeline will be run

        """
        return self.kf_dict['kfdefaultns']

    def get_appport(self):
        """
        Function for giving application port to the caller of the function

        Args:None

        Returns:
            appport: port number on which kfadapter will be hosted

        """
        return self.appport

    def get_runstspollinterval(self):
        """
        Function for giving run_status_polling_interval_sec to caller of the function

        Args:None

        Returns:
            run_status_polling_interval_sec: time in secs before run status will be queried
                                             again from kubeflow

        """
        return self.run_status_polling_interval_sec

    def is_config_loaded_properly(self):
        """
        Function for determining whether any of configuration parameters are none i.e not loaded

        Args:None

        Returns:
                True if all config params are set properly
                False otherwise

        """
        return all(v is not None for v in [self.appport, self.run_status_polling_interval_sec,\
                self.kf_dict['kfdefaultns'], self.trainingmgr_dict['trainingmgr_host'],\
                self.trainingmgr_dict['trainingmgr_port'], self.kf_dict['kfhostname'], self.kf_dict['kfport']])
