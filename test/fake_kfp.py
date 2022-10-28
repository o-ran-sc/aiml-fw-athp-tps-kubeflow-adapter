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

from typing import Optional

from kfp_server_api.models.api_list_pipeline_versions_response import ApiListPipelineVersionsResponse
from kfp_server_api.models.api_pipeline_version import ApiPipelineVersion
from kfp_server_api.models.api_experiment import ApiExperiment
from kfp_server_api.models.api_run_detail import ApiRunDetail
from kfp_server_api.models.api_run import ApiRun



import kfp_server_api

class FakeKfp:
    def list_experiments(self,
            page_token='',
            page_size=10,
            sort_by='',
            namespace=None):
        return None

    def get_experiment(self,
                       experiment_id=None,
                       experiment_name=None,
                       namespace=None):

        exp = ApiExperiment()
        exp.id = 'ex-id'
        exp.name = 'exp-name'
        return exp 

    
    def upload_pipeline_version(
        self,
        pipeline_package_path,
        pipeline_version_name: str,
        pipeline_id: Optional[str] = None,
        pipeline_name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        return None

    def get_run(self, run_id: str):
        rundetail = ApiRunDetail()
        run = ApiRun()
        run._id = 'id'
        run._name = 'name'
        run._status = 'status'
        rundetail._run = run
        return None
    """
    def list_runs(self,
                  page_token='',
                  page_size=10,
                  sort_by='',
                  experiment_id=None,
                  namespace=None,
                  filter=None):
        
        listrun = ApiListRunsResponse()
        run1 = ApiRun()
        run1.id(self, 'id')
        run1.description(self, 'description') 
        run1.status(self, 'status')  
        rr0 = ApiResourceReference()
        rr0.name(self, 'name')
        key0 = ApiResourceKey()
        key0.id(self, 'id')
        rr0.key(self, key0)
  
        rr1 = ApiResourceReference()
        rr1.name(self, 'name')
        key1 = ApiResourceKey()
        key1.id(self, 'id')
        rr1.key(key1)
    
        run1.resource_references(self, rr0)
        listrun.runs(self, [run1]) 
    
        return listrun
    """


    #def get_kf_pipeline_id(self, pipeline_name):
     #   return None

    def list_pipeline_versions(
            self,
            pipeline_id: str,
            page_token: str = '',
            page_size: int = 10,
            sort_by: str = ''
    ):
        response = ApiListPipelineVersionsResponse()
        version1 = ApiPipelineVersion()
        version1.name = 'version_name'
        version1.id = 'version_id'
        version2 = ApiPipelineVersion()
        version2.name = 'version_name'
        version2.id = 'version_id'
        response._versions = [version1, version2]
        response._total_size = 1
        return response

   # def get_kf_pipeline_version_id(self, pipeline_id, pipeline_version_name):
    #    return None

    def run_pipeline(
        self,
        experiment_id: str,
        job_name: str,
        pipeline_package_path: Optional[str] = None,
        params: Optional[dict] = None,
        pipeline_id: Optional[str] = None,
        version_id: Optional[str] = None,
        pipeline_root: Optional[str] = None,
        enable_caching: Optional[str] = None,
        service_account: Optional[str] = None,
    ):
        return None
    

    def delete_pipeline(self, pipeline_id):
        return None

    def get_pipeline(self, pipeline_id: str):
        return None

    def list_pipelines(self,
                       page_token='',
                       page_size=10,
                       sort_by=''):
        return None
    

    def upload_pipeline(
        self,
        pipeline_package_path: str = None,
        pipeline_name: str = None,
        description: str = None,
    ):
        return None

    def get_pipeline_id(self, name):
        
        return ['pipelin_id', 'pipelin_id2',]


class FakeNegativeKfp:
    """ def list_pipeline_versions(
            self,
            pipeline_id: str,
            page_token: str = '',
            page_size: int = 10,
            sort_by: str = ''
    ):
        return None """

    """
    def upload_pipeline(
        self,
        pipeline_package_path: str = None,
        pipeline_name: str = None,
        description: str = None,
    ):
        return None
    """
    """
    def list_pipeline_versions(
            self,
            pipeline_id: str,
            page_token: str = '',
            page_size: int = 10,
            sort_by: str = ''
    ):
        response = ApiListPipelineVersionsResponse()
        version1 = ApiPipelineVersion()
        version1.name = 'version_name'
        version1.id = 'version_id'
        version2 = ApiPipelineVersion()
        version2.name = 'version_name'
        version2.id = 'version_id'
        response._versions = [version1, version2]
        response._total_size = None
        return response
    """
    def get_pipeline_id(self, name):
        raise kfp_server_api.exceptions.ApiException(name)

    def get_experiment(self,
                       experiment_id=None,
                       experiment_name=None,
                       namespace=None):
        raise ValueError(
                'Either experiment_id or experiment_name is required') 
    
class FakeAdditionalKfp:
    """
    def list_pipeline_versions(
            self,
            pipeline_id: str,
            page_token: str = '',
            page_size: int = 10,
            sort_by: str = ''
    ):
        response = ApiListPipelineVersionsResponse()
        version1 = ApiPipelineVersion()
        version1.name = 'version_name'
        version1.id = 'version_id'
        version2 = ApiPipelineVersion()
        version2.name = 'version_name'
        version2.id = 'version_id'
        response._versions = [version1, version2]
        response._total_size = None
        return response
    """
    """
    def get_pipeline_id(self, name):
        return None
        
    def upload_pipeline(
        self,
        pipeline_package_path: str = None,
        pipeline_name: str = None,
        description: str = None,
    ):
        return None
        """

