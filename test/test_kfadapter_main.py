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
import json 

from flask_api import status

from kfadapter import kfadapter_main
from kfadapter.tmgr_logger import TMLogger
from .fake_kfconnect import FakeKfConnect, NegativeFakeAdditionalKfConnect, NegativeFakeKfConnect, NegativeFakeNoneKfConnect
from .fake_kfconf import FakeKfConf

class Test_pipeline_id_operations:
    
    def setup_method(self):
        kfadapter_main.LOGGER = TMLogger("config/log_config.yaml").logger
        kfadapter_main.KFCONNECT_KF_OBJ = FakeKfConnect()
        kfadapter_main.KFCONNECT_CONFIG_OBJ = FakeKfConf.get_instance()
        self.client = kfadapter_main.APP.test_client(self)

    def test_get_experiment(self): 
        experiment_name = "ai-server"
        response = self.client.get("/experiments/{}".format(experiment_name))
        expected_data = b'{"name": "ai-server", "id":"isj0t3jdhf"}'

        assert response.content_type == "application/json", "not equal content type"
        assert response.status_code == status.HTTP_200_OK, "not equal code"
    
    def test_get_all_runs(self):
        response = self.client.get("/runs")
        assert response.content_type == "application/json", "not equal content type"
        assert response.status == '200 OK'
    
    def test_get_pipeline_id(self): 
        pipeline_name = "car-racing"
        response = self.client.get("/pipelineIds/{}".format(pipeline_name))
        expected_data = b'{"name":"car-racing", "id":"3jfidhsueuf2oj"}'

        assert response.content_type == "application/json", "not equal content type"
        assert response.status_code == status.HTTP_200_OK, "not equal code"
    
    def test_upload_pipeline(self):
        pipeline_file_name="Training-Manager/kf_connector/test/pipeline.zip"
        
        response = self.client.post("/user/2/edit", data={
        "file": pipeline_file_name,
        "description": "description"
        })
        
        assert response.content_type == "text/html; charset=utf-8"        
    
    def test_get_run(self):
        run_id = "run_id"
        response = self.client.get("/runs/{}".format(run_id))

        assert response.content_type == "application/json", "not equal content type"
        assert response.status == '200 OK'
    
    def test_get_pipeline_version(self):
        pipeline_name="car-racing"

        response = self.client.get("/pipelines/{}/versions".format(pipeline_name))
        expected_data = ""

        assert response.content_type == "application/json", "not equal content type"
        assert response.status_code == status.HTTP_200_OK, "not equal code"

    def test_delete_run(self):
        run_id = "run_id"
        response = self.client.delete("/runs/{}".format(run_id))

        assert response.content_type == "application/json", "not equal content type"
        assert response.status == '400 BAD REQUEST'
    
    def test_get_pipelines(self):
        response = self.client.get("/pipelines")
        assert response.content_type == "application/json", "not equal content type"
        assert response.status_code == status.HTTP_200_OK
    
    def test_delete_pipelines(self):
        pipeline_id = "pipelineIdsample"

        response = self.client.delete("/pipelines/{}".format(pipeline_id))
        expected_data = b'{"OK"}'

        assert response.content_type == "application/json"
        assert response.status_code == status.HTTP_200_OK
    
    def test_check_liveness(self):
        response = self.client.get("/liveness")
        expected_data = b'Okay'
        assert response.content_type == "text/html; charset=utf-8", "not equal content type"
        assert response.data == expected_data

    def test_get_experiments(self):
        response = self.client.get("/experiments")
        expected_data=""
        assert response.content_type == "application/json", "not equal content type"

    def test_execute_job(self):
        job_name = "job_name"
        dict_job = {'arguments' :  {'key1':'value1', 'key2':'value2'}, 'pipeline_name' :  "pipeline_name", 'experiment_name' : "experiment_name", 'pipeline_version' : "pipeline_version"}
        payload = json.dumps(dict_job)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        response = self.client.post("/trainingjobs/{}/execution".format(job_name), data=payload, headers=headers)
        assert response.content_type == "application/json", "not equal content type"
        
    def test_get_pipelines_id(self):
        pipeline_id = "pipelineIdsample"
        response = self.client.get("/pipelines/{}".format(pipeline_id))

        assert response.content_type == "application/json", "not equal content type"
        assert response.status_code == status.HTTP_200_OK, "not equal code"

class Test_Negative:
    def setup_method(self):
        self.client = kfadapter_main.APP.test_client(self)
        kfadapter_main.LOGGER = TMLogger("config/log_config.yaml").logger

        kfadapter_main.KFCONNECT_KF_OBJ = NegativeFakeKfConnect()
        kfadapter_main.KFCONNECT_CONFIG_OBJ = FakeKfConf.get_instance()

    def test_negative_get_pipeline_version(self):
        pipeline_name="car-racing"

        response = self.client.get("/pipelines/{}/versions".format(pipeline_name))
        assert response.content_type == "text/html; charset=utf-8", "not equal content type"

    def test_negative_get_pipelines_id(self):
        pipeline_id = "pipelineIdsample"
        response = self.client.get("/pipelines/{}".format(pipeline_id))

        assert response.content_type == "application/json", "not equal content type"
        assert response.status_code == 500, "not equal code"
    
    def test_negative_get_pipeline_id(self): 
        pipeline_name = "car-racing"
        response = self.client.get("/pipelineIds/{}".format(pipeline_name))

        assert response.content_type == "application/json"
    
    def test_negative_get_experiment(self):
        experiment_name = "ai-server"
        response = self.client.get("/experiments/{}".format(experiment_name))
        expected_data = b'{"name": "ai-server", "id":"isj03jdhf"}'

        assert response.content_type == "application/json", "not equal content type"
        assert response.status_code == 400, "not equal code" 

    def test_negative_get_run(self):
        run_id = "run_id"
        response = self.client.get("/runs/{}".format(run_id))

        assert response.content_type == "application/json", "not equal content type"
        assert response.status == '400 BAD REQUEST'
        
    def test_negative_upload_pipeline(self):
        pipeline_file_name="pipeline.zip"
        description="test pipeline"
        pipeline_name="car-racing"

        dict_pipeline = {'file' : pipeline_file_name, 'description' : description}
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        
        response = self.client.post("pipelineIds/{}".format(pipeline_name), data=json.dumps(dict_pipeline), headers=headers)

        assert response.content_type == "application/json"
        assert response.status == '500 INTERNAL SERVER ERROR'

    def test_negative_get_all_runs(self):
        response = self.client.get("/runs")
        assert response.content_type == "application/json", "not equal content type"
        assert response.status == '400 BAD REQUEST'

    def test_negative_get_pipelines(self):
        response = self.client.get("/pipelines")
        print(response)
        assert response.content_type == "application/json", "not equal content type"
        assert response.status_code == 500

    def test_negative_execute_job(self):
        job_name = "job_name"
        dict_job = {}
        dict_job['arguments'] = "param1"
        dict_job['pipeline_name'] = "pipeline_name"
        dict_job['experiment_name'] = "experiment_name"
        dict_job['pipeline_version'] = "pipeline_version"
        payload = json.dumps(dict_job)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        response = self.client.post("/trainingjobs/{}/execution".format(job_name), data=payload, headers=headers)
        assert response.content_type == "application/json", "not equal content type"

class TestAdditionalKfConnector:
    def setup_method(self):
        self.client = kfadapter_main.APP.test_client(self)
        kfadapter_main.LOGGER = TMLogger("config/log_config.yaml").logger
        kfadapter_main.KFCONNECT_KF_OBJ = NegativeFakeAdditionalKfConnect()
        kfadapter_main.KFCONNECT_CONFIG_OBJ = FakeKfConf.get_instance()
    
    def test_negative_exception_get_kf_experiment(self):
        experiment_name = "ai-server"
        response = self.client.get("/experiments/{}".format(experiment_name))

        assert response.content_type == "application/json", "not equal content type"
        
    def test_negative_exception_get_pipeline_id(self):
        pipeline_name = "car-racing"
        response = self.client.get("/pipelineIds/{}".format(pipeline_name))

        assert response.content_type == "text/html; charset=utf-8", "not equal content type"
        
    def test_negative_exception_get_pipeline_version(self):
        pipeline_name="car-racing"
        response = self.client.get("/pipelines/{}/versions".format(pipeline_name))
        assert response.content_type == "application/json", "not equal content type"
        
    def test_negative_exception_execute_job(self):
        job_name = "job_name"
        dict_job = {}
        dict_job['arguments'] = {"param3":"value3", "param4":"value4"}
        dict_job['pipeline_name'] = 'pipeline_name'
        dict_job['experiment_name'] = 'experiment_name'
        dict_job['pipeline_version'] = 'pipeline_version'
        payload = json.dumps(dict_job)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        response = self.client.post("/trainingjobs/{}/execution".format(job_name), data=payload, headers=headers)
        assert response.content_type == "application/json", "not equal content type"
        
    def test_negative_get_experiments(self):
        response = self.client.get("/experiments")
        expected_data=""
        assert response.content_type == "application/json", "not equal content type"
    
    def test_negative_exception_get_pipelines_id(self):
        pipeline_id = "pipelineIdsample"
        response = self.client.get("/pipelines/{}".format(pipeline_id))

        assert response.content_type == "application/json", "not equal content type"
        assert response.status_code == 500, "not equal code"


class TestNoneKfConnect:
    def setup_method(self):
        self.client = kfadapter_main.APP.test_client(self)
        kfadapter_main.LOGGER = TMLogger("config/log_config.yaml").logger
        kfadapter_main.KFCONNECT_KF_OBJ = NegativeFakeNoneKfConnect()
        kfadapter_main.KFCONNECT_CONFIG_OBJ = FakeKfConf.get_instance()
        
    def test_nagetive_none_execute_job(self):
        job_name = "job_name"
        dict_job = {}
        dict_job['arguments'] = "param1"
        dict_job['pipeline_name'] = "pipeline_name"
        dict_job['experiment_name'] = "experiment_name"
        dict_job['pipeline_version'] = "pipeline_version"
        payload = json.dumps(dict_job)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        response = self.client.post("/trainingjobs/{}/execution".format(job_name), data=payload, headers=headers)
        assert response.content_type == "application/json", "not equal content type"
    