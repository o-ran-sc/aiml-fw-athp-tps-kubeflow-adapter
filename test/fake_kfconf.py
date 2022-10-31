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

from kfadapter.tmgr_logger import TMLogger

class FakeKfConf:
    __instance = None

    def get_instance():
        if FakeKfConf.__instance is None:
            FakeKfConf()

        return FakeKfConf.__instance

    def __init__(self):
        FakeKfConf.__instance = self

        self.kf_dict = {}
        self.ucmgr_dict = {}
        self.tmgr_logger = TMLogger("config/log_config.yaml")
        self.logger = self.tmgr_logger.logger

        self.run_status_polling_interval_sec = 20
        self.kf_dict['kfhostname'] = 'kfhostname'
        self.kf_dict['kfport'] = 9999
        self.kf_dict['kfdefaultns'] = 'ai-server'
        self.appport = 7777
        self.ucmgr_dict['ucmgr_host'] = '127.0.0.1'
        self.ucmgr_dict['ucmgr_port'] = 30025
