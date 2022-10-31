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

import sys
sys.path.append("kfadapter")
# import kfadapter_conf
from kfadapter_kfconnect import KfConnect
from fake_kfconnect import FakeKfConnect
from fake_kfp import FakeKfp
from fake_kfp import FakeNegativeKfp
import kfp_server_api

class Test_KfConnect:
    def setup_method(self):
        self.__KFCONNECT = KfConnect()
        self.__KFCONNECT .set_kf_client(FakeKfp())

    def test_get_kf_list_experiments(self):
        assert None ==  self.__KFCONNECT.get_kf_list_experiments(nspace="")
    
    def test_get_kf_experiment_details(self):
        assert 'exp-name' == self.__KFCONNECT.get_kf_experiment_details(ex_name='ai-server', nspace='ai-server').name

    def test_get_kf_run(self):
        assert None == self.__KFCONNECT.get_kf_run(run_id='run_id')
    """
    def test_get_kf_list_run(self):
        expected_data = {'pipeline_runtime': None,'run': {'created_at': None,'description': None,'error': None,'scheduled_at': None, 'service_account': None,'status': 'status','storage_state': None}}
        assert expected_data == self.__KFCONNECT.get_kf_list_runs(nspace='ai-server')
    """
    def test_get_kf_list_pipelines(self):
        assert None == self.__KFCONNECT.get_kf_list_pipelines()

    def test_get_kf_pipeline_id(self):
        assert ['pipelin_id', 'pipelin_id2'] == self.__KFCONNECT.get_kf_pipeline_id(pipeline_name='pipeline_name')

    def test_get_kf_pipeline_version_id(self):
        assert None != self.__KFCONNECT.get_kf_pipeline_version_id(pipeline_id='pipeline_id', pipeline_version_name='version_name')

    def test_upload_kf_pipeline(self):
        assert None == self.__KFCONNECT.upload_kf_pipeline(pipeline_name='pipeline_name', file='file', desc='desc')
    
    def test_upload_pipeline_with_versions(self):
        assert None == self.__KFCONNECT.upload_pipeline_with_versions(pipeline_name='pipeline_name', file='file', desc='desc')

    def test_negative_upload_pipeline_with_versions(self):
        self.__KFCONNECT.set_kf_client(FakeNegativeKfp())
        try:
            assert None == self.__KFCONNECT.upload_pipeline_with_versions(pipeline_name='pipeline_name', file='file', desc='desc')
        except kfp_server_api.exceptions.ApiException as err :
            print(err)

    def test_additional_upload_pipeline_with_versions(self):
        assert None == self.__KFCONNECT.upload_pipeline_with_versions(pipeline_name='pipeline_name', file='file', desc='desc')

    def test_get_pl_versions_by_pl_name(self):
        assert None != self.__KFCONNECT.get_pl_versions_by_pl_name(pipeline_name='pipeline_name')

    def test_negative_get_pl_versions_by_pl_name(self):
        try:
            assert None != self.__KFCONNECT.get_pl_versions_by_pl_name(pipeline_name='pipeline_name')
        except kfp_server_api.exceptions.ApiException as err :
            print(err)

    def test_get_kf_pipeline_desc(self):
        assert None == self.__KFCONNECT.get_kf_pipeline_desc(pipeline_id='pipeline_id')

    def test_delete_kf_pipeline(self):
        assert None == self.__KFCONNECT.delete_kf_pipeline(pipeline_id='pipeline_id')

    def test_run_kf_pipeline(self):
        assert None == self.__KFCONNECT.run_kf_pipeline(exp_id='exp_id', pipeline_id='pipeline_id', arguments='arguments', version_id='version_id')
    

class Test_Negative_KfConnect:
    def setup_method(self):
        print("test")
        self.__KFCONNECT = KfConnect()
        self.__KFCONNECT .set_kf_client(FakeNegativeKfp())
        
    def test_negative_get_kf_experiment_details(self):
        assert None == self.__KFCONNECT.get_kf_experiment_details(ex_name='ai-server', nspace='ai-server')