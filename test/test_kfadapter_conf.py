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

import os

from kfadapter import kfadapter_conf

class Test_kfadapter_conf:
    KUBEFLOW_HOST_NAME = '127.0.0.1'
    KUBEFLOW_PORT_NUM = '8088'
    KF_NAMESPACE = 'namespace'
    KF_ADAPTER_PORT_NUM = '3333'
    TRAINING_MGR_HOST = '127.0.0.1'
    TRAINING_MGR_PORT_NUM = '1111'
    
    def setup_method(self):
        os.environ['KUBEFLOW_HOST'] = self.KUBEFLOW_HOST_NAME
        os.environ['KUBEFLOW_PORT'] = self.KUBEFLOW_PORT_NUM
        os.environ['KF_NAMESPACE'] = self.KF_NAMESPACE
        os.environ['KF_ADAPTER_PORT'] = self.KF_ADAPTER_PORT_NUM
        os.environ['TRAININGMGR_HOST'] = self.TRAINING_MGR_HOST
        os.environ['TRAININGMGR_PORT'] = self.TRAINING_MGR_PORT_NUM
        self.KFCONNECT_CONFIG_OBJ = kfadapter_conf.KfConfiguration.get_instance()    
    
    def test_get_hostname(self):
        ret = self.KFCONNECT_CONFIG_OBJ.get_kfhostname()
        assert ret == self.KUBEFLOW_HOST_NAME
        
    def test_get_kfport(self):
        ret = self.KFCONNECT_CONFIG_OBJ.get_kfport()
        assert ret == self.KUBEFLOW_PORT_NUM
    
    def test_get_trainingmgrhost(self):
        ret = self.KFCONNECT_CONFIG_OBJ.get_trainingmgrhost()
        assert ret == self.TRAINING_MGR_HOST
        
    def test_get_trainingmgrport(self):
        ret = self.KFCONNECT_CONFIG_OBJ.get_trainingmgrport()
        assert ret == self.TRAINING_MGR_PORT_NUM
        
    def test_get_kfnamespace(self):
        ret = self.KFCONNECT_CONFIG_OBJ.get_kfnamespace()
        assert ret == self.KF_NAMESPACE
        
    def test_get_appport(self):
        ret = self.KFCONNECT_CONFIG_OBJ.get_appport()
        assert ret == self.KF_ADAPTER_PORT_NUM
        
    def test_get_runstspollinterval(self):
        ret = self.KFCONNECT_CONFIG_OBJ.get_runstspollinterval()
        assert ret == 20
    
    def test_is_config_loaded_properly(self):
        ret = self.KFCONNECT_CONFIG_OBJ.is_config_loaded_properly()
        assert ret != None
        
        