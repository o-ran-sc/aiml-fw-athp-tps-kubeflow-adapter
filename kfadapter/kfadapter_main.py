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

"""kfadapter_main.py.

This is the main files and it  exposes various rest endpoints for
HTTP GET - for getting experiments,runs,pipelines,experiment details,
           pipeline description,run description(TBD)
HTTP POST - for execution of pipeline


"""

import os
import traceback
import json
from threading import Thread

from flask import Flask, request, jsonify
from flask_api import status
import kfp_server_api

from kfadapter import kfadapter_conf
from kfadapter.kfadapter_kfconnect import KfConnect
from kfadapter.kfadapter_util import BadRequest, wait_status_thread, keys_match, check_map

#Handles to Config and Kubeflow
KFCONNECT_CONFIG_OBJ = None
KFCONNECT_KF_OBJ = None
LOGGER = None


APP = Flask(__name__)

@APP.errorhandler(BadRequest)
def handle_bad_request(error):
    """
    Function handling BadRequest exception globally,
    serialize into JSON, and respond with 400.
    """
    print(error.payload)
    payload = dict(error.payload or ())
    payload['status'] = error.status
    payload['message'] = error.message

    return jsonify(payload), error.status

@APP.route("/experiments/<expname>")
def get_experiment(expname):
    """Function handling HTTP GET rest endpoint to get experiment details from kubeflow

    Args:
        expname (str): Experiment name

    Returns:
        json dict: denoting expid for expname
        status: HTTP status 200 or 400

    Exceptions:
        error payload describing status, message and HTTP status code

    """
    exp_dict = {}
    try:
        exp = KFCONNECT_KF_OBJ.get_kf_experiment_details(expname,\
                KFCONNECT_CONFIG_OBJ.kf_dict['kfdefaultns'])

        if exp is None:
            raise ValueError("Experiment name is not correct " +expname)

        LOGGER.debug("Experiment name is present")

        LOGGER.debug(exp)
        exp_dict['name'] = exp.name
        exp_dict['id'] = exp.id
    except ValueError as err:
        LOGGER.error(err)
        raise BadRequest('Experiment name does not exist', status.HTTP_400_BAD_REQUEST,\
                {'payload': {'exp.name': expname}}) from None
    except:# pylint: disable=bare-except
        tbk = traceback.format_exc()
        LOGGER.error(tbk)
        raise BadRequest('Unsupported error from Kubeflow',\
                status.HTTP_500_INTERNAL_SERVER_ERROR, {'ext': 1}) from None

    return jsonify(exp_dict), status.HTTP_200_OK

@APP.route("/pipelineIds/<pipe_name>", methods=['GET', 'POST'])
def get_pipeline_id(pipe_name):
    """Function handling HTTP GET rest endpoint to get pipeline id from kubeflow

    Args:
        pipe_name (str): Pipeline name

    Returns:
        json dict: denoting pipline_id for pipeline_name
        status: HTTP status 200 or 400

    Exceptions:
        error payload describing status, message and HTTP status code

    """
    pipe_dict = {}
    try:
        if request.method == 'GET':
            pipe_id = KFCONNECT_KF_OBJ.get_kf_pipeline_id(pipe_name)
            if pipe_id is None:
                raise ValueError("No pipeline is found with name "+ pipe_name)

            LOGGER.debug(pipe_id)
            pipe_dict['name'] = pipe_name
            pipe_dict['id'] = pipe_id
        else:
            uploaded_file = request.files['file']
            LOGGER.debug("Uploading received for %s", uploaded_file.filename)
            if uploaded_file.filename != '':
                uploaded_file_path = "/tmp/" + uploaded_file.filename
                uploaded_file.save(uploaded_file_path)
                LOGGER.debug("File uploaded :%s", uploaded_file_path)
                description = request.form['description']
                pipe_info = KFCONNECT_KF_OBJ.upload_pipeline_with_versions(
                    pipe_name,
                    uploaded_file_path,
                    description)
                LOGGER.debug("Pipeline uploaded :%s", pipe_name)
                pipe_dict['name'] = pipe_name
                pipe_dict['id'] = pipe_info.id
                os.remove(uploaded_file_path)
            else:
                raise Exception("Error saving file from POST")
    except ValueError as err:
        LOGGER.error(err)
        raise BadRequest('PipeLine Name does not exist', status.HTTP_400_BAD_REQUEST,\
                {'payload': {'pipe_name': pipe_name, 'error': str(err)}}) from None
    except kfp_server_api.exceptions.ApiException as err:
        LOGGER.error("Exception from KubeFlow")
        LOGGER.error(err)
        os.remove(uploaded_file_path)
        raise BadRequest(check_map(json.loads(err.body), "error_details"),\
                status.HTTP_500_INTERNAL_SERVER_ERROR) from None
    except: # pylint: disable=bare-except
        tbk = traceback.format_exc()
        LOGGER.error(tbk)
        raise BadRequest('Unsupported error from Kubeflow',\
                status.HTTP_500_INTERNAL_SERVER_ERROR, {'ext': 1}) from None

    return jsonify(pipe_dict), status.HTTP_200_OK

@APP.route("/pipelines/<pipeline_name>/versions", methods=['GET'])
def get_versions_for_pipeline(pipeline_name):
    """
    Function handling HTTP GET rest endpoint to get pipeline versions based on
       pipeline name.

    Args:
        pipeline_name (str): Pipeline name

    Returns:
        json dict:
            it contains versions list for given pipeline name

        status: HTTP status 200

    Exceptions:
        error payload describing status, message and HTTP status code
    """
    result_dict = {}
    try:
        versions_list = KFCONNECT_KF_OBJ.get_pl_versions_by_pl_name(
            pipeline_name)
    except kfp_server_api.exceptions.ApiException as err:
        LOGGER.error("Exception from KubeFlow")
        LOGGER.error(err)
        raise BadRequest(check_map(json.loads(err.body), "error_details"),\
                status.HTTP_500_INTERNAL_SERVER_ERROR) from None
    except: # pylint: disable=bare-except
        tbk = traceback.format_exc()
        LOGGER.error(tbk)
        raise BadRequest('Unsupported error from Kubeflow',\
                status.HTTP_500_INTERNAL_SERVER_ERROR, {'ext': 1}) from None
    result_dict['versions_list'] = versions_list
    return jsonify(result_dict), status.HTTP_200_OK


@APP.route("/pipelines/<pipe_id>", methods=['GET', 'DELETE'])
def get_pipeline(pipe_id):
    """Function handling HTTP GET/DELETE rest endpoint to get/delete pipeline based on
       pipeline id from kubeflow

    Args:
        pipe_id (str): Pipeline id

    Returns:
        json dict:
                   denoting pipline description for pipeline_id in HTTP GET METHOD
                   denoting pipeline and status for pipeline_id in HTTP DELETE METHOD

        status: HTTP status 200 or 400

    Exceptions:
        error payload describing status, message and HTTP status code

    """
    pipe_dict = {}
    pipe_arg = {}
    try:
        if request.method == 'DELETE':
            pipeline_info = KFCONNECT_KF_OBJ.delete_kf_pipeline(pipe_id)
            pipeline_info = {}
            if bool(pipeline_info) is False:
                pipe_dict['id'] = pipe_id
                pipe_dict['status'] = "Deleted"
        else:
            pipeline_info = KFCONNECT_KF_OBJ.get_kf_pipeline_desc(pipe_id)
            LOGGER.debug(pipeline_info)
            for parameter in pipeline_info.parameters:
                pipe_arg[parameter.name] = parameter.value
            pipe_dict['arguments'] = pipe_arg
            pipe_dict['description'] = pipeline_info.description
            pipe_dict['id'] = pipeline_info.id
            pipe_dict['name'] = pipeline_info.name
    except kfp_server_api.exceptions.ApiException as err:
        LOGGER.error("Exception from KubeFlow")
        LOGGER.error(err)
        raise BadRequest('Unsupported error from Kubeflow',\
                status.HTTP_500_INTERNAL_SERVER_ERROR, {'payload': {'pipe_id': pipe_id}}) from None

    return jsonify(pipe_dict), status.HTTP_200_OK


@APP.route("/liveness")
def kf_liveness():
    """Function handling liveness probe

    Args:none

    Returns:
        status: HTTP status 200

    """
    return "Okay", status.HTTP_200_OK

@APP.route("/experiments")
def list_experiments():
    """Function handling rest endpoint to get all experiments
       from kubeflow

    Args:none

    Returns:
        json dict:
                   denoting experiment id  for each experiment name

        status: HTTP status 200 or 400

    Exceptions:
        error payload describing status, message and HTTP status code

    """

    exp_dict = {}
    try:
        exp = KFCONNECT_KF_OBJ.get_kf_list_experiments(KFCONNECT_CONFIG_OBJ.kf_dict['kfdefaultns'])
        for experiment in exp.experiments:
            exp_dict[experiment.name] = experiment.id
    except:# pylint: disable=bare-except
        tbk = traceback.format_exc()
        LOGGER.error(tbk)
        raise BadRequest('Unsupported error from Kubeflow',\
                status.HTTP_500_INTERNAL_SERVER_ERROR, {'ext': 1}) from None

    return jsonify(exp_dict), status.HTTP_200_OK

@APP.route("/pipelines")
def list_pipelines():
    """Function handling rest endpoint to get all pipelines
       from kubeflow

    Args:none

    Returns:
        json dict:
                   denoting pipeline description for each pipeline

        status: HTTP status 200 or 400

    Exceptions:
        error payload describing status, message and HTTP status code

    """
    pipe_dict = {}
    try:
        pipeline_list = KFCONNECT_KF_OBJ.get_kf_list_pipelines()

        for pipeline in pipeline_list.pipelines:
            pipe_super_dict = {}
            pipe_param_dict = {}
            pipe_super_dict['id'] = pipeline.pipeline_id
            pipe_super_dict['description'] = pipeline.description
            pipe_dict[pipeline.display_name] = pipe_super_dict
    except:# pylint: disable=bare-except
        tbk = traceback.format_exc()
        LOGGER.error(tbk)
        raise BadRequest('Unsupported error from Kubeflow',\
                status.HTTP_500_INTERNAL_SERVER_ERROR, {'ext': 1}) from None

    return jsonify(pipe_dict), status.HTTP_200_OK

@APP.route('/trainingjobs/<trainingjob_name>/execution', methods=['POST'])
def run_pipeline(trainingjob_name):
    """Function handling HTTP POST rest endpoint to execute pipeline based on trainingjob name

    Args:
        trainingjob_name (str): Unique trainingjob_name
        json_request_args(dict):
                            arguments(dict) - Arguments required for pipeline to run
                            pipeline_name(str) - name of Pipeline registered in KubeFlow
                            experiment_name(str) - Experiment under which the pipeline
                                                   run will happen


    Returns:
        json dict: denoting run for pipeline
        status: HTTP status 200 or 400

    Exceptions:
        error payload describing status, message and HTTP status code

    """
    errcode = None
    err_string = None
    LOGGER.debug("run_pipeline for %s", trainingjob_name)
    run_dict = {}
    try:
        errcode = status.HTTP_400_BAD_REQUEST
        err_string = "Internal Error"
        req = request.json
        LOGGER.debug(req)
        if("arguments" in req.keys() and "pipeline_name" in req.keys() and \
                "experiment_name" in req.keys()):
            arguments = req["arguments"]
            pipe_name = req["pipeline_name"]
            exp_name = req["experiment_name"]
            pipeline_version_name = req["pipeline_version"]

            errcode = status.HTTP_500_INTERNAL_SERVER_ERROR
            err_string = "Unsupported error from Kubeflow"
            exp = KFCONNECT_KF_OBJ.get_kf_experiment_details(exp_name,\
                    KFCONNECT_CONFIG_OBJ.kf_dict['kfdefaultns'])
            if exp is None:
                raise ValueError("Experiment name is not correct " +exp_name)

            LOGGER.debug(exp)
            pipe_id = KFCONNECT_KF_OBJ.get_kf_pipeline_id(pipe_name)
            if pipe_id is None:
                raise ValueError("Pipeline name is not correct " +pipe_name)

            LOGGER.debug("Pipeline ID = " + pipe_id)

            pipe_arg = {}
            LOGGER.debug("Getting pipeline desc")

            pipeline_info = KFCONNECT_KF_OBJ.get_kf_pipeline_desc(pipe_id)
            LOGGER.debug(pipeline_info)
            for parameter in pipeline_info.default_version.parameters:
                pipe_arg[parameter.name] = parameter.value
            LOGGER.debug("Arguments provided " + str(arguments.keys()))
            LOGGER.debug("Arguments in pipeline " + str(pipe_arg.keys()))
            args_match = keys_match(arguments, pipe_arg)
            if args_match is False:
                LOGGER.error("arguments: "+str(arguments))
                LOGGER.error("pipe_arg: "+str(pipe_arg))
                raise ValueError("Arguments does not match with pipeline arguments")

            version_id = KFCONNECT_KF_OBJ.get_kf_pipeline_version_id(pipe_id, pipeline_version_name)
            LOGGER.debug("Running pipeline")
            run = KFCONNECT_KF_OBJ.run_kf_pipeline(exp.id, pipe_id, arguments, version_id)
            LOGGER.debug("Run ID = %s", run.id)
            run_dict['trainingjob_name'] = trainingjob_name
            run_dict['run_id'] = run.id
            run_dict['run_name'] = run.name
            run_dict['experiment_name'] = run.resource_references[0].name
            run_dict['experiment_id'] = run.resource_references[0].key.id

            if len(run.resource_references) > 1:
                run_dict['pipeline_name'] = run.resource_references[1].name
                run_dict['pipeline_id'] = run.resource_references[1].key.id

            if run.status is None:
                run_dict['run_status'] = "scheduled"
                with kfadapter_conf.LOCK:
                    kfadapter_conf.TRAINING_DICT[run.id] = trainingjob_name
        else:
            errcode = status.HTTP_400_BAD_REQUEST
            err_string = 'Less arguments'
            raise BadRequest('Less arguments', errcode, {'ext':1})
    except ValueError as err:
        LOGGER.error(err)
        payload = {'payload': request.json}
        raise BadRequest(err_string, errcode, payload) from None

    except:# pylint: disable=bare-except
        tbk = traceback.format_exc()
        if err_string == 'Internal Error':
            LOGGER.error(tbk)
            payload = {'ext': 1}
        else:
            payload = {'payload': request.json}

        raise BadRequest(err_string, errcode, payload) from None

    return jsonify(run_dict), status.HTTP_200_OK

@APP.route("/runs")
def list_runs():
    """Function handling rest endpoint to get all runs
       from kubeflow

    Args:none

    Returns:
        json dict:
                   denoting run description for each pipeline run

        status: HTTP status 200 or 400

    Exceptions:
        error payload describing status, message and HTTP status code

    """
    run_dict = {}

    try:
        runs = KFCONNECT_KF_OBJ.get_kf_list_runs(KFCONNECT_CONFIG_OBJ.kf_dict['kfdefaultns'])

        for run in runs.runs:
            run_super_dict = {}
            run_super_dict['run_id'] = run.id
            run_super_dict['run_description'] = run.description
            run_super_dict['run_status'] = run.status
            run_super_dict['experiment_name'] = run.resource_references[0].name
            run_super_dict['experiment_id'] = run.resource_references[0].key.id

            if len(run.resource_references) > 1:
                run_super_dict['pipeline_name'] = run.resource_references[1].name
                run_super_dict['pipeline_id'] = run.resource_references[1].key.id

            run_dict[run.name] = run_super_dict
    except:# pylint: disable=bare-except
        tbk = traceback.format_exc()
        LOGGER.error(tbk)
        raise BadRequest('Unsupported error from Kubeflow', status.HTTP_400_BAD_REQUEST,
                         {'ext': 1}) from None


    return jsonify(run_dict), status.HTTP_200_OK

@APP.route("/runs/<run_id>", methods=['GET', 'DELETE'])
def kf_run(run_id):
    """Function handling HTTP GET/DELETE rest endpoint to get/delete run based on
       run id from kubeflow

    Args:
        run_id (str): Run id

    Returns:
        json dict:
                   denoting run description for run_id in HTTP GET METHOD
                   denoting run and status for pipeline_id in HTTP DELETE METHOD

        status: HTTP status 200 or 400

    Exceptions:
        error payload describing status, message and HTTP status code

    """
    run_dict = {}
    try:
        if request.method == 'DELETE':
            LOGGER.error("Method not supported yet")
            raise BadRequest("Method not supported yet", status.HTTP_501_NOT_IMPLEMENTED,\
                   {'ext': 1})

        run_info = KFCONNECT_KF_OBJ.get_kf_run(run_id)
        run_dict['run_id'] = run_info.run_id
        run_dict['run_name'] = run_info.display_name
        run_dict['run_status'] = run_info.state
        LOGGER.debug(run_dict)
    except Exception as err:
        LOGGER.error("Exception from KubeFlow in run")
        LOGGER.error(err)
        raise BadRequest('Unsupported error from Kubeflow', status.HTTP_400_BAD_REQUEST,\
                {'payload': {'run_id': run_id}}) from None

    return jsonify(run_dict), status.HTTP_200_OK

if __name__ == "__main__":
    KFCONNECT_CONFIG_OBJ = kfadapter_conf.KfConfiguration.get_instance()
    if KFCONNECT_CONFIG_OBJ.is_config_loaded_properly() is False:
        print("Config not loaded properly")
    else:
        KF_HOST_URI = "http://"+KFCONNECT_CONFIG_OBJ.kf_dict['kfhostname']+\
                    ":"+KFCONNECT_CONFIG_OBJ.kf_dict['kfport']+"/pipeline"
        LOGGER = KFCONNECT_CONFIG_OBJ.logger
        LOGGER.debug(KF_HOST_URI)
        KFCONNECT_KF_OBJ = KfConnect()
        try:
            KFCONNECT_KF_OBJ.get_kf_client(KF_HOST_URI)
            LOGGER.debug(KFCONNECT_CONFIG_OBJ.appport)
            THR = Thread(target=wait_status_thread, args=(1, KFCONNECT_KF_OBJ))
            THR.start()
            APP.run(host='0.0.0.0', port=KFCONNECT_CONFIG_OBJ.appport)
        except Exception as some_err:# pylint: disable=broad-except
            LOGGER.error(some_err)
