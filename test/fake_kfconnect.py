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

import kfp_server_api
from kfp_server_api.models.api_run import ApiRun
from kfp_server_api.models.api_list_runs_response import ApiListRunsResponse

from kfp_server_api.models.api_experiment import ApiExperiment
from kfp_server_api.models.api_list_pipelines_response import ApiListPipelinesResponse
from kfp_server_api.models.api_pipeline import ApiPipeline
from kfp_server_api.models.api_parameter import ApiParameter
from kfp_server_api.models.api_resource_reference import ApiResourceReference
from kfp_server_api.models.api_resource_key import ApiResourceKey
from kfp_server_api.models.api_pipeline_version import ApiPipelineVersion

class FakeKfConnect:

    def __init__(self):
        print("Initialized Fake KfConnect")

    def get_kf_list_experiments(self, nspace):
        explist = kfp_server_api.ApiListExperimentsResponse()
        
        exp = kfp_server_api.ApiExperiment()
        exp.name = "name"
        exp.id = "id"
        explist.experiments = [exp]
        return explist

    def get_pl_versions_by_pl_name(self, pipeline_name):
        version_list = []
        version_list.append("2.0.0")
        return version_list
    """
    def run_kf_pipeline(self,exp_id,arguments,
        experiment_id: str,
        job_name: str,
        pipeline_package_path: Optional[str] = None,
        params: Optional[dict] = None,
        pipeline_id: Optional[str] = None,
        version_id: Optional[str] = None,
        pipeline_root: Optional[str] = None,
        enable_caching: Optional[str] = None,
        service_account: Optional[str] = None,):
        
        run = ApiRun()
        run.id = "run_id"
        run.name = "run_name"
        rr0 = ApiResourceReference()
        rr0.name = "rr0"
        key0 = ApiResourceKey()
        key0.id = "id0"
        rr0.key = key0
        rr1 = ApiResourceReference()
        rr1.name = "rr0"
        key1 = ApiResourceKey()
        key1.id = "id1"
        rr1.key = key1
        run.status = "Running"
        run.resource_references = [rr0, rr1]
        return run
    """

    def delete_kf_pipeline(self, pipeline_id):
        return True
    
    def get_kf_pipeline_version_id( self,pipeline_version_name,
            pipeline_id: str,
            page_token: str = '',
            page_size: int = 10,
            sort_by: str = ''
    ):
        return "pipeline_id"

    def get_kf_list_runs(self,
                  page_token='',
                  page_size=10,
                  sort_by='',
                  experiment_id=None,
                  namespace=None):
        listrun = ApiListRunsResponse()
        run1 = ApiRun()
        run1.id = "id" 
        run1.description = "description" 
        run1.status = "status"  
        
        rr0 = ApiResourceReference()
        rr0.name = "rr0"
        key0 = ApiResourceKey()
        key0.id = "id"
        rr0.key = key0
  
        rr1 = ApiResourceReference()
        rr1.name = "rr1"
        key1 = ApiResourceKey()
        key1.id = "id"
        rr1.key = key1
    
        run1.resource_references = [rr0, rr1]
        
        run2 = ApiRun()
        run2.id = "id" 
        run2.description = "description" 
        run2.status = "status"  
        
        rr2 = ApiResourceReference()
        rr2.name = "rr2"
        key2 = ApiResourceKey()
        key2.id = "id"
        rr2.key = key2
  
        rr3 = ApiResourceReference()
        rr3.name = "rr1"
        key3 = ApiResourceKey()
        key3.id = "id"
        rr3.key = key3
    
        run2.resource_references = [rr2, rr3]
        
        
        listrun.runs = [run1, run2]
    
        return listrun

    def get_kf_pipeline_desc(self, pipeline_id: str):
        pipeline_info = ApiPipeline()
        
        param1 = ApiParameter()
        param1.name = "param1"
        param1.value = "value1"
        param2 = ApiParameter()
        param2.name = "param2"
        param2.value = "value2"
        pipeline_info.parameters = [param1, param2]
        pipeline_info.description = 'description'
        pipeline_info.id = "id"
        pipeline_info.name = "name"
        
        param3 = ApiParameter()
        param3.name = "param3"
        param3.value = "value3"
        param4 = ApiParameter()
        param4.name = "param4"
        param4.value = "value4"
        
        default_version = ApiPipelineVersion()
        default_version.parameters = [param3, param4]    
           
        pipeline_info.default_version = default_version
        return pipeline_info

    def get_kf_run(self, run_id: str):
        run = ApiRun()
        run.name = "run_name"
        run.status = "Running"
        run.id = "run_id"
        return run

    def get_kf_experiment_details(self, ex_name, nspace):
        experiment = ApiExperiment()
        experiment.name = "exp_name"
        experiment.id = "exp_id"
        return experiment

    def get_kf_pipeline_id(self, pipeline_name):
        return "pipeline_id"
    """
    def upload_pipeline_with_versions(self, pipeline_name, file, desc):
        pipeline_info = kfp_server_api.ApiPipelineVersion()
        pipeline_info.id("pipeline_id")
        return pipeline_info   
    """ 

    def get_kf_list_pipelines(self):
        pipeline_list = ApiListPipelinesResponse()
        pipeline = ApiPipeline()
        pipeline.id = "pipeline_id"
        pipeline.description = "pipeline_description"
        parameter = ApiParameter()
        parameter.name = "param1"
        parameter.value = "value1"
        pipeline.parameters = [parameter]
        pipeline_list.pipelines = [pipeline]
        return pipeline_list


class NegativeFakeKfConnect:
    def __init__(self):
        print("Initialized Negative Fake KfConnect")

    def get_kf_pipeline_id(self, pipeline_name):
        return None

    def get_kf_experiment_details(self, ex_name, nspace):
        return None

    def get_pl_versions_by_pl_name(self, pipeline_name):
        raise kfp_server_api.exceptions.ApiException
    
    def get_kf_run(self, run_id):
        """
        run = ApiRun()
        run.id = run_id
        run.name = 'run_name'
        run.status = 'Running'
        return run        
        """
        raise Exception('erro')

    def get_kf_list_runs(self, nspace):
        
        run = ApiRun()
        run.name = "run_name"
        run.status = "Running"
        run.id = "run_id"
        run.description = "descrption"
        rr0 = ApiResourceReference()
        rr0.name = "rr0"
        key0 = ApiResourceKey()
        key0.id = "key0id"  
        run.resource_references = [rr0]

        runs = ApiListRunsResponse()
        runs.runs = [run]
        
        return runs

    def get_kf_list_pipelines(self,
                       page_token='',
                       page_size=10,
                       sort_by=''):
        raise Exception('error')
      

    def get_kf_pipeline_desc(self, pipeline_id):
        raise kfp_server_api.exceptions.ApiException 
    
class NegativeFakeAdditionalKfConnect:
    
    def get_kf_experiment_details(self, ex_name, nspace):
        raise Exception('error')
    
    def get_kf_pipeline_id(self, pipeline_name):
        raise kfp_server_api.exceptions.ApiException('error')
    """
    def get_pl_versions_by_pl_namee(self, pipeline_name):
        raise Exception('error')
    """
    """
    def get_kf_pipeline_version_id(self, pipeline_id, pipeline_version_name):
        raise Exception('error')
    """
    def get_kf_list_experiments(self, nspace):
        raise Exception('error')

    def get_kf_pipeline_desc(self, pipeline_id: str):
         raise kfp_server_api.exceptions.ApiException('error') 

class NegativeFakeNoneKfConnect:
    
    def get_kf_experiment_details(self, ex_name, nspace):
        experiment = ApiExperiment()
        experiment.name = "exp_name"
        experiment.id = "exp_id"
        return experiment
    
    def get_kf_pipeline_id(self, pipeline_name):
        return None
    
    
    
    
