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
import io
from unittest import TestCase
from mock import patch, MagicMock
from flask_api import status

import kfp_server_api
from kfp_server_api.models.v2beta1_run import V2beta1Run as ApiRun
from kfp_server_api.models.v2beta1_list_runs_response import V2beta1ListRunsResponse as ApiListRunsResponse
from kfp_server_api.models.v2beta1_experiment import V2beta1Experiment as ApiExperiment
from kfp_server_api.models.v2beta1_list_pipelines_response import V2beta1ListPipelinesResponse as ApiListPipelinesResponse
from kfp_server_api.models.v2beta1_pipeline import V2beta1Pipeline as ApiPipeline
from kfp_server_api.models.v2beta1_runtime_config import V2beta1RuntimeConfig as ApiParameter
from kfp_server_api.models.v2beta1_pipeline_version import V2beta1PipelineVersion as ApiPipelineVersion
from kfadapter import kfadapter_main
from kfadapter import kfadapter_conf
from kfadapter import kfadapter_kfconnect

class testKfadapterApi(TestCase):
    @classmethod
    def setUpClass(self):
        kfadapter_main.KFCONNECT_CONFIG_OBJ = kfadapter_conf.KfConfiguration.get_instance()
        kfadapter_main.LOGGER = kfadapter_main.KFCONNECT_CONFIG_OBJ.logger
        kfadapter_main.KFCONNECT_KF_OBJ = kfadapter_kfconnect.KfConnect()

        self.client = kfadapter_main.APP.test_client(self)


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_experiment_details")
    def test_get_experiment(self, mock_get_kf_experiment_details):
        # given
        exp = ApiExperiment()
        exp.display_name = "exp-name"
        exp.experiment_id = "exp-id"
        mock_get_kf_experiment_details.return_value = exp

        # when
        response = self.client.get("/experiments/{}".format(exp.display_name))

        # then
        mock_get_kf_experiment_details.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["name"], exp.display_name)
        self.assertEqual(response.get_json()["id"], exp.experiment_id)


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_list_runs")
    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_pipeline_desc")
    def test_get_all_runs(self, mock_get_kf_pipeline_desc, mock_get_kf_list_runs):
        class PipelineVersionReference:
            def __init__(self, pipeline_id, pipeline_version_id):
                self.pipeline_id = pipeline_id
                self.pipeline_version_id = pipeline_version_id

        # given
        runs = [ApiRun() for _ in range(2)]
        for i, run in enumerate(runs):
            run.run_id = "runid"
            run.display_name = f"run-name{i}"
            run.description = "description"
            run.state = "status"
            run.pipeline_version_reference = PipelineVersionReference(
                pipeline_id=f"pipeline-id{i}",
                pipeline_version_id=f"pipeline-version-id{i}"
            )
            run.experiment_id = f"experiment-id{i}"

        list_run = ApiListRunsResponse()
        list_run.runs = runs
        mock_get_kf_list_runs.return_value = list_run

        # Mocking get_kf_pipeline_desc to return a mock pipeline info
        def mock_pipeline_desc(pipeline_id):
            pipeline = MagicMock()
            pipeline.display_name = f"pipeline-name{pipeline_id[-1]}"
            pipeline.pipeline_id = pipeline_id
            return pipeline

        mock_get_kf_pipeline_desc.side_effect = mock_pipeline_desc

        # when
        response = self.client.get("/runs")
        print('response:', response.get_data())

        # then
        mock_get_kf_list_runs.assert_called_once()
        mock_get_kf_pipeline_desc.assert_any_call("pipeline-id0")
        mock_get_kf_pipeline_desc.assert_any_call("pipeline-id1")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.get_data(),
            b'{"run-name0":{"experiment_id":"experiment-id0","pipeline_id":"pipeline-id0","pipeline_name":"pipeline-name0","run_description":"description","run_id":"runid","run_status":"status"},"run-name1":{"experiment_id":"experiment-id1","pipeline_id":"pipeline-id1","pipeline_name":"pipeline-name1","run_description":"description","run_id":"runid","run_status":"status"}}\n'
        )

    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_pipeline_id")
    def test_get_pipeline_id(self, mock_get_kf_pipeline_id):
        # given
        pipeline_name = "pipeline-name"
        pipeline_id = "pipeline-id"
        mock_get_kf_pipeline_id.return_value = pipeline_id

        # when
        response = self.client.get("/pipelineIds/{}".format(pipeline_name))

        # then
        mock_get_kf_pipeline_id.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["id"], pipeline_id)
        self.assertEqual(response.get_json()["name"], pipeline_name)


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.upload_pipeline_with_versions")
    def test_upload_pipeline(self, mock_upload_pipeline_with_versions):
        # given
        pipeline_name = "pipeline-name"
        pipeline_id = "pipeline-id"

        pipeline_info = ApiPipeline()
        pipeline_info.pipeline_id = pipeline_id
        mock_upload_pipeline_with_versions.return_value = pipeline_info

        files = {}
        files['file'] = (io.BytesIO(b"pipeline-file"), 'pipeline')
        files['description'] = "pipeline-description"

        # when
        response = self.client.post("pipelineIds/{}".format(pipeline_name), data=files, content_type="multipart/form-data")

        # then
        mock_upload_pipeline_with_versions.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()['name'], pipeline_name)
        self.assertEqual(response.get_json()['id'], pipeline_id)


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_pl_versions_by_pl_name")
    def test_get_pipeline_version(self, mock_get_pl_versions_by_pl_name):
        # given
        pipeline_name="pipeline-name"
        version_list = ["1.0.0"]
        mock_get_pl_versions_by_pl_name.return_value = version_list

        # when
        response = self.client.get("/pipelines/{}/versions".format(pipeline_name))

        # then
        mock_get_pl_versions_by_pl_name.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["versions_list"], version_list)


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_run")
    def test_get_run(self, mock_get_kf_run):
        # given
        run = ApiRun()
        run.run_id = "run-id"
        run.display_name = "run-name"
        run.state = "Running"
        mock_get_kf_run.return_value = run

        # when
        response = self.client.get("/runs/{}".format(run.run_id))

        # then
        mock_get_kf_run.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["run_id"], run.run_id)
        self.assertEqual(response.get_json()["run_name"], run.display_name)
        self.assertEqual(response.get_json()["run_status"], run.state)


    def test_delete_run(self):
        # given
        run_id = "run-id"

        # when
        response = self.client.delete("/runs/{}".format(run_id))

        # then
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_list_pipelines")
    def test_get_pipelines(self, mock_get_kf_list_pipelines):

       #given
        pipeline = ApiPipeline()
        pipeline.pipeline_id = "pipeline-id"
        pipeline.description = "pipeline-description"
        pipeline.display_name= "pipeline-name"
        pipeline.created_at = "created-at"


        pipeline_list = ApiListPipelinesResponse()
        pipeline_list.pipelines = [pipeline]
        pipeline_list.next_page_token = "next-page-token"
        pipeline_list.total_size = "total-size"

        mock_get_kf_list_pipelines.return_value = pipeline_list

        # when
        response = self.client.get("/pipelines")

        # then
        mock_get_kf_list_pipelines.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_data(),
                         b'{"next_page_token":"next-page-token","pipelines":[{"created_at":"created-at","description":"pipeline-description","display_name":"pipeline-name","pipeline_id":"pipeline-id"}],"total_size":"total-size"}\n')



    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_pipeline_desc")
    def test_get_pipeline(self, mock_get_kf_pipeline_desc):
        # given
        pipeline_name = "pipeline-name"
        pipeline_id = "pipeline-id"

        params = [ ApiParameter() for _ in range(4)]
        for i, param in enumerate(params) :
            param.name = "param-name{}".format(i)
            param.value = "param-value{}".format(i)

        pipeline_info = ApiPipeline()
        pipeline_info.parameters = [params[0], params[1]]
        pipeline_info.description = "description"
        pipeline_info.id = pipeline_name
        pipeline_info.name = pipeline_id

        default_version = ApiPipelineVersion()
        default_version.parameters = [params[2], params[3]]
        pipeline_info.default_version = default_version
        mock_get_kf_pipeline_desc.return_value = pipeline_info

        # when
        response = self.client.get("/pipelines/{}".format(pipeline_id))

        # then
        mock_get_kf_pipeline_desc.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_data(), b'{"arguments":{"param-name0":"param-value0","param-name1":"param-value1"},"description":"description","id":"pipeline-name","name":"pipeline-id"}\n')


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.delete_kf_pipeline")
    def test_delete_pipelines(self, mock_delete_kf_pipeline):
        # given
        pipeline_id = "pipeline-id"
        mock_delete_kf_pipeline.return_value = True

        # when
        response = self.client.delete("/pipelines/{}".format(pipeline_id))

        # then
        mock_delete_kf_pipeline.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["id"], pipeline_id)
        self.assertEqual(response.get_json()["status"], "Deleted")


    def test_check_liveness(self):
        # when
        response = self.client.get("/liveness")

        # then
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_data(), b'Okay')


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_list_experiments")
    def test_get_experiments(self, mock_get_kf_list_experiments):
        # given
        exp = ApiExperiment()
        exp.display_name = "exp-name"
        exp.experiment_id = "exp-id"

        explist = kfp_server_api.V2beta1ListExperimentsResponse()
        explist.experiments = [exp]
        mock_get_kf_list_experiments.return_value = explist

        # when
        response = self.client.get("/experiments")

        # then
        mock_get_kf_list_experiments.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()[exp.display_name], exp.experiment_id)


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_experiment_details")
    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_pipeline_id")
    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_pipeline_version_id")
    @patch("kfadapter.kfadapter_kfconnect.KfConnect.run_kf_pipeline")
    def test_execute_job(self, mock_run_kf_pipeline, mock_get_kf_pipeline_version_id, mock_get_kf_pipeline_id, mock_get_kf_experiment_details):
        # given
        exp = ApiExperiment()
        exp.display_name = "exp-name"
        exp.experiment_id = "exp-id"
        mock_get_kf_experiment_details.return_value = exp

        pipeline_name = "pipeline-name"
        pipeline_id = "pipeline-id"
        mock_get_kf_pipeline_id.return_value = pipeline_id

        params = [ ApiParameter() for _ in range(4)]
        for i, param in enumerate(params) :
            param.name = "param-name{}".format(i)
            param.value = "param-value{}".format(i)

        pipeline_info = ApiPipeline()
        pipeline_info.parameters = [params[0], params[1]]
        pipeline_info.description = "pipeline-description"
        pipeline_info.id = pipeline_name
        pipeline_info.name = pipeline_id

        mock_get_kf_pipeline_version_id.return_value = pipeline_id

        run = {}
        run["display_name"] = "run-name"
        run["run_id"] = "run-id"
        pipeline_id= "pipeline_id"
        pipeline_version_reference= {'pipeline_id': pipeline_id,
                                'pipeline_version_id': pipeline_id}
        run["pipeline_version_reference"]=pipeline_version_reference

        run["state"] = "RUNNING"
        mock_run_kf_pipeline.return_value = run


        job_name = "job_name"
        dict_job = {}
        args = {}
        args[params[2].name] = params[2].value
        args[params[3].name] = params[3].value
        dict_job["arguments"] = args
        dict_job["pipeline_name"] = pipeline_name
        dict_job["pipeline_version"] = "2.0.0"
        dict_job["experiment_name"] = exp.display_name

        # when
        response = self.client.post("/trainingjobs/{}/execution".format(job_name), data=json.dumps(dict_job), headers={'content-type': 'application/json', 'Accept-Charset': 'UTF-8'})

        # then
        mock_get_kf_experiment_details.assert_called_once()
        mock_get_kf_pipeline_id.assert_called_once()
        mock_get_kf_pipeline_version_id.assert_called_once()
        mock_run_kf_pipeline.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        # todo
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.get_data(), b'{"experiment_id":"rr-id0","experiment_name":"rr-name0","pipeline_id":"rr-id1","pipeline_name":"rr-name1","run_id":"run-id","run_name":"run-name","trainingjob_name":"job_name"}\n')

class testNegativeKfadapterApi(TestCase):
    @classmethod
    def setUpClass(self):
        kfadapter_main.KFCONNECT_CONFIG_OBJ = kfadapter_conf.KfConfiguration.get_instance()
        kfadapter_main.LOGGER = kfadapter_main.KFCONNECT_CONFIG_OBJ.logger
        kfadapter_main.KFCONNECT_KF_OBJ = kfadapter_kfconnect.KfConnect()

        self.client = kfadapter_main.APP.test_client(self)


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_pl_versions_by_pl_name")
    def test_negative_get_versions_for_pipeline_failed_with_api_exception(self, mock_get_pl_versions_by_pl_name):
        # given
        pipeline_name="pipeline-name"
        mock_get_pl_versions_by_pl_name.side_effect = kfp_server_api.exceptions.ApiException

        # when
        response = self.client.get("/pipelines/{}/versions".format(pipeline_name))

        # then
        mock_get_pl_versions_by_pl_name.assert_called_once()
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_pl_versions_by_pl_name")
    def test_negative_get_versions_for_pipeline_failed_with_unsupported_error(self, mock_get_pl_versions_by_pl_name):
        # given
        pipeline_name="pipeline-name"
        mock_get_pl_versions_by_pl_name.side_effect = IndexError("")

        # when
        response = self.client.get("/pipelines/{}/versions".format(pipeline_name))

        # then
        mock_get_pl_versions_by_pl_name.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.get_json()["message"], "Unsupported error from Kubeflow")
        self.assertEqual(response.get_json()["ext"], 1)


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_pipeline_desc")
    def test_negative_get_pipeline_failed_with_api_exception(self, mock_get_kf_pipeline_desc):
        # given
        pipeline_id = "pipeline-id"
        mock_get_kf_pipeline_desc.side_effect = kfp_server_api.exceptions.ApiException

        # when
        response = self.client.get("/pipelines/{}".format(pipeline_id))

        # then
        mock_get_kf_pipeline_desc.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.get_json()["message"],"Unsupported error from Kubeflow")
        self.assertEqual(response.get_json()["payload"],{"pipe_id":pipeline_id})


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_pipeline_id")
    def test_negative_get_pipeline_id_failed_with_value_error(self, mock_get_kf_pipeline_id):
        # given
        pipeline_name = "pipeline-name"
        mock_get_kf_pipeline_id.return_value = None

        # when
        response = self.client.get("/pipelineIds/{}".format(pipeline_name))

        # then
        mock_get_kf_pipeline_id.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.get_json()["message"],"PipeLine Name does not exist")
        self.assertEqual(response.get_json()["payload"],{"error":"No pipeline is found with name pipeline-name","pipe_name":pipeline_name})


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.upload_pipeline_with_versions")
    def test_negative_upload_pipeline_failed_with_api_exception(self, mock_upload_pipeline_with_versions):
        # given
        pipeline_name = "pipeline-name"

        mock_upload_pipeline_with_versions.side_effect = kfp_server_api.exceptions.ApiException

        files = {}
        files['file'] = (io.BytesIO(b"pipeline-file"), 'pipeline.zip')
        files['description'] = "pipeline-description"

        # when
        response = self.client.post("pipelineIds/{}".format(pipeline_name), data=files, content_type="multipart/form-data")

        # then
        mock_upload_pipeline_with_versions.assert_called_once()
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


    def test_negative_upload_pipeline_failed_cause_empty_file_name(self):
        # given
        pipeline_name = "pipeline-name"

        files = {}
        files['file'] = (io.BytesIO(b"pipeline-file"), '')

        # when
        response = self.client.post("pipelineIds/{}".format(pipeline_name), data=files, content_type="multipart/form-data")

        # then
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.get_json()["message"],"Unsupported error from Kubeflow")
        self.assertEqual(response.get_json()["ext"], 1)


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_experiment_details")
    def test_negative_get_experiment_failed_cause_no_such_experiment(self, mock_get_kf_experiment_details):
        # given
        exp_name = "exp-name"
        mock_get_kf_experiment_details.return_value = None

        # when
        response = self.client.get("/experiments/{}".format(exp_name))

        # then
        mock_get_kf_experiment_details.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.get_json()["message"],"Experiment name does not exist")
        self.assertEqual(response.get_json()["payload"],{"exp.name":exp_name})


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_experiment_details")
    def test_negative_get_experiment_failed_with_unsupported_error(self, mock_get_kf_experiment_details):
        # given
        exp_name = "exp-name"
        mock_get_kf_experiment_details.return_value = IndexError("")

        # when
        response = self.client.get("/experiments/{}".format(exp_name))

        # then
        mock_get_kf_experiment_details.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.get_json()["message"], "Unsupported error from Kubeflow")
        self.assertEqual(response.get_json()["ext"], 1)


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_run")
    def test_negative_get_run_failed_with_exception(self, mock_get_kf_run):
        # given
        run_id = "run-id"
        mock_get_kf_run.side_effect = Exception("")

        # when
        response = self.client.get("/runs/{}".format(run_id))

        # then
        mock_get_kf_run.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.get_json()["message"],"Unsupported error from Kubeflow")
        self.assertEqual(response.get_json()["payload"],{"run_id":run_id})


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_list_runs")
    def test_negative_get_all_runs_failed_with_unsupported_error(self, mock_get_kf_list_runs):
        # given
        mock_get_kf_list_runs.side_effect = IndexError("")

        # when
        response = self.client.get("/runs")

        # then
        mock_get_kf_list_runs.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.get_json()["message"], "Unsupported error from Kubeflow")
        self.assertEqual(response.get_json()["ext"], 1)


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_list_pipelines")
    def test_negative_get_pipelines_failed_with_unsupported_error(self, mock_get_kf_list_pipelines):
        # given
        mock_get_kf_list_pipelines.side_effect = IndexError("")

        # when
        response = self.client.get("/pipelines")

        # then
        mock_get_kf_list_pipelines.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.get_json()["message"], "Unsupported error from Kubeflow")
        self.assertEqual(response.get_json()["ext"], 1)


    def test_negative_execute_job_failed_cause_less_arguments(self):
        # given
        job_name = "job_name"
        dict_job = {}

        # when
        response = self.client.post("/trainingjobs/{}/execution".format(job_name), data=json.dumps(dict_job), headers={'content-type': 'application/json', 'Accept-Charset': 'UTF-8'})

        # then
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.get_json()["message"], "Less arguments")
        self.assertFalse(response.get_json()["payload"])


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_experiment_details")
    def test_negative_execute_job_failed_cause_no_such_experiment(self, mock_get_kf_experiment_details):
        mock_get_kf_experiment_details.return_value = None

        job_name = "job_name"
        dict_job = {}

        params = [ ApiParameter() for _ in range(2)]
        for i, param in enumerate(params) :
            param.name = "param-name{}".format(i)
            param.value = "param-value{}".format(i)

        args = {}
        args[params[0].name] = params[0].value
        args[params[1].name] = params[1].value

        dict_job["arguments"] = args
        dict_job["pipeline_name"] = "pipeline-name"
        dict_job["pipeline_version"] = "2.0.0"
        dict_job["experiment_name"] = "exp-name"

        # when
        response = self.client.post("/trainingjobs/{}/execution".format(job_name), data=json.dumps(dict_job), headers={'content-type': 'application/json', 'Accept-Charset': 'UTF-8'})

        # then
        mock_get_kf_experiment_details.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.get_json()["message"], "Unsupported error from Kubeflow")


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_experiment_details")
    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_pipeline_id")
    def test_negative_execute_job_failed_cause_no_such_pipeline(self, mock_get_kf_pipeline_id, mock_get_kf_experiment_details):
        exp = ApiExperiment()
        exp_name = "exp-name"
        exp.id = "exp-id"
        mock_get_kf_experiment_details.return_value = exp

        mock_get_kf_pipeline_id.return_value = None

        job_name = "job_name"
        dict_job = {}

        params = [ ApiParameter() for _ in range(2)]
        for i, param in enumerate(params) :
            param.name = "param-name{}".format(i)
            param.value = "param-value{}".format(i)

        args = {}
        args[params[0].name] = params[0].value
        args[params[1].name] = params[1].value

        dict_job["arguments"] = args
        dict_job["pipeline_name"] = "pipeline-name"
        dict_job["pipeline_version"] = "2.0.0"
        dict_job["experiment_name"] = exp_name

        # when
        response = self.client.post("/trainingjobs/{}/execution".format(job_name), data=json.dumps(dict_job), headers={'content-type': 'application/json', 'Accept-Charset': 'UTF-8'})

        # then
        mock_get_kf_experiment_details.assert_called_once()
        mock_get_kf_pipeline_id.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.get_json()["message"], "Unsupported error from Kubeflow")


    @patch("kfadapter.kfadapter_kfconnect.KfConnect.get_kf_list_experiments")
    def test_negative_get_experiments_failed_with_unsupported_error(self, mock_get_kf_list_experiments):
        # given
        mock_get_kf_list_experiments.return_value = IndexError("")

        # when
        response = self.client.get("/experiments")

        # then
        mock_get_kf_list_experiments.assert_called_once()
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.get_json()["message"], "Unsupported error from Kubeflow")
        self.assertEqual(response.get_json()["ext"], 1)
