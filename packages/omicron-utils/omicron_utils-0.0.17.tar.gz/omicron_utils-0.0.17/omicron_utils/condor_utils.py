#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: nu:ai:ts=4:sw=4

#
#  Copyright (C) 2025 Joseph Areeda <joseph.areeda@ligo.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Provides functions to query job attributes in an HTCondor batch processing system.

This module contains utility functions to filter and retrieve job information from
an HTCondor batch processing scheduler. Queries can be performed using regex patterns,
cluster IDs, or constraints for more targeted results. Results are formatted according
to the specified projections, enabling flexible data extraction.
"""

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'

import getpass
import platform
from pathlib import Path
from time import sleep, time

import htcondor2 as htcondor
from htcondor2 import HTCondorException


def get_schedd(schedd_spec=None):
    """
    Retrieve an htcondor.Schedd instance based on the provided specification.

    This function returns an instance of `htcondor.Schedd`. When no specification
    is provided, it defaults to return the default `htcondor.Schedd` object.

    :param str|None schedd_spec: The specification for the scheduler usually a fqdn. If `None`, the default
        `htcondor.Schedd` instance is returned. Optional.
    :return: An `htcondor.Schedd` instance based on the provided specification.
    """
    schedd_spec = None
    for i in range(10):
        try:
            if schedd_spec is None:
                schedd_spec = htcondor.Schedd()
            else:
                schedd_spec = htcondor.Schedd(schedd_spec)
            break
        except Exception as e:
            print(f'Try #{i+1}: error connecting to schedd: {e}')
            sleep(10)
    if schedd_spec is None:
        raise HTCondorException('Unable to connect to schedd')
    return schedd_spec


def schedd_query(constraint=None, schedd=None, projection=None,):
    """
        Query scheduler for jobs
    :param string constraint: Constrint expression eg: "ClusterID == 1234"
    :param htcondor2._schedd.Schedd|str|None schedd: Schedd object or name of schedd or None for default
    :param str|None projection: Projection expression eg: "ClusterId, ProcId, JobBatchName, JobStatus
    :return list[dict]: matching jobs, may be empty
    """
    schedd = get_schedd(schedd)

    if projection is None:
        projection = ["ClusterId", "ProcId", "JobBatchName", "JobStatus"]

    ret = schedd.query(projection=projection, constraint=constraint)
    ret = list(ret) if ret else []
    return ret


def query_by_name(name, schedd=None, projection=None,):
    """
    Query the schedd for the value of a classad attribute
    :param str name: regex pattern to match against JobBatchName. EG: '.*online.*PEM1.*'
    :param htcondor.Schedd schedd: schedd to query
    :param list[str] projection: A list of classad attributes to return,
                                 defaults to ["ClusterId", "ProcId", "JobBatchName", "JobStatus"]
    :return: list of matching Job attributes containing the name
    """

    constraint = f'regexp("{name}", JobBatchName)'
    return schedd_query(constraint=constraint, schedd=schedd, projection=projection)


def query_by_clusterid(clusterid, procid=None, schedd=None, projection=None, ):
    """
    Retrieves information about a specific cluster of jobs in a batch processing scheduler.
    This function queries a scheduler using the provided cluster ID and retrieves relevant
    job information defined by the projection.

    :param clusterid: The unique cluster ID used to identify the batch of jobs.
    :type clusterid: int

    :param procid: The unique process ID used to identify a specific job within a cluster.
    :type procid: int

    :param schedd: The scheduler object to perform the query on. If not provided, a
        default scheduler will be used. Optional.
    :type schedd: object, optional

    :param projection: The list of attributes to include in the query result. Defaults
        to ["ClusterId", "ProcId", "JobBatchName", "JobStatus"].
    :type projection: list[str]

    :return: A list of job details matching the given cluster ID.
    :rtype: list[dict]
    """

    cid = clusterid
    constraint = f'ClusterId == {cid}'
    if procid and '.' not in str(clusterid):
        constraint += f' && ProcId == {procid}'
    if projection is None:
        projection = ["ClusterId", "ProcId", "JobBatchName", "JobStatus"]
    qres = schedd_query(constraint=constraint, schedd=schedd, projection=projection)
    return qres


def wait_for_job(job_str, schedd=None, sleep_time=5, timeout=None, ):
    """
    Waits for the completion of a given job.

    This function monitors the status of a given job and waits until the job
    is completed. Use this function when there is a need to ensure that the
    execution of the code can only proceed after the job has finished.

    :param job_str: The job name or cluster id whose completion status is to be monitored.
    :type job_str: str|number
    :param sleep_time: polling interval in seconds
    :type sleep_time: int
    :param schedd: The scheduler object to perform the query on. If not provided, a
    :type schedd: object or schedd name, optional
    :param timeout: timeout in seconds
    :type timeout: int
    :return: Returns when thejob is no longer found in the scheduler
    :rtype: None
    """
    start = time()
    job_str = str(job_str)
    while query_by_clusterid(job_str, schedd=schedd) or query_by_name(job_str, schedd=schedd):
        sleep(sleep_time)
        elapsed = time() - start
        if timeout and elapsed >= timeout:
            raise TimeoutError(f'Timeout waiting for job {job_str} to complete')


def condor_submit_job(submit_file, schedd=None):
    """
    Submit a job to an HTCondor scheduler using a specified submit file.

    This function reads the content of the submit file to create a Submit object,
    then queues the job in the HTCondor scheduler provided. It returns the cluster ID
    of the submitted job and the results of the job submission process.

    :param submit_file: The path to the HTCondor submit file. It contains the
        job's description and requirements.
    :type submit_file: str|Path
    :param schedd: The HTCondor Schedd object to which the job will be submitted.
        If not specified, a default scheduler is used.
    :type schedd: optional[htcondor.Schedd]
    :return: A tuple containing the cluster ID of the submitted job as an integer
        and the submission result as an object indicating the details of the submission.
    :rtype: tuple[int, object]
    """

    submit_path = Path(submit_file)
    # Load the submit spec file
    with submit_path.open() as f:
        submit_description = f.read()

    # Parse it into a Submit object
    submit = htcondor.Submit(submit_description)

    cluster_id, submit_result = condor_queue_job(submit, schedd=schedd)
    return cluster_id, submit_result


def condor_queue_job(submit, count=1, schedd=None):
    """
    Submit a job or multiple jobs to the Condor scheduler.

    This function allows submission of one or more jobs to a Condor scheduler,
    returning the cluster ID associated with the job(s) and the submission result.
    A scheduler is optionally specified; otherwise, a default scheduler is used.

    :param submit: The job submission object defining job parameters and configurations.
    :param count: An optional integer specifying the number of jobs to submit,
        with a default of 1.
    :param schedd: An optional Condor scheduler object. If not provided,
        a default scheduler is retrieved and utilized.
    :return: A tuple where the first element is the cluster ID associated with
        the submission and the second element is the submission result.
    """
    schedd = get_schedd(schedd)
    if platform.machine() == 'arm64':
        submit.update({'requirements': '(Target.ARCH == "X86_64" || Target.ARCH == "ARM64")'})

    if count > 1:
        res = schedd.submit(submit, count=count)
    else:
        res = schedd.submit(submit)
    return res.cluster(), res


def condor_submit_dag(dag_file, schedd=None, options=True, use_strict=3, name=None):
    """
    Submit a DAG job to HTCondor with optional configurations.

    This function allows for the submission of Directed Acyclic Graph (DAG)
    jobs to an HTCondor system. The DAG submission file can be customized
    with additional options, strictness modes can be set for `dagman`, and a
    specific batch name can optionally be provided.

    :param dag_file: Path to the DAG file to be submitted.
    :type dag_file: str|Path
    :param schedd: HTCondor schedd object to which the job will be submitted.
                   If not provided, the default scheduler is used.
                   Optional.
    :type schedd: htcondor.Schedd or None
    :param options: Either a dictionary of additional submission options
                    or a boolean indicating whether to use default options.
                    Optional.
    :type options: dict or bool
    :param use_strict: Strictness level for DAGMan, where the default value
                       is set to '3'.
                       Optional.
    :type use_strict: int
    :param name: (Optional) Custom batch name for submission operations
                 overriding the default DAG basename.
    :type name: str or None
    :return: Tuple containing the cluster ID of the submitted DAG job
             and the submission result information.
    :rtype: tuple[int, dict]
    """
    dag_path = Path(dag_file)
    if not dag_path.exists():
        raise FileNotFoundError(f'DAG file: {dag_file} does not exist')
    dag_path.resolve()
    dag_file = str(dag_path.absolute())

    if name is not None:
        batch_name = name
    else:
        batch_name = f'{dag_path.stem} $(ClusterID)'
    default_options = {'batch-name': batch_name, 'force': 'True', 'import_env': 'True'}

    try:
        if isinstance(options, dict):
            dag_sub = htcondor.Submit.from_dag(str(dag_path.absolute()), options=options)
        elif isinstance(options, bool) and options:
            if options:
                dag_sub = htcondor.Submit.from_dag(dag_file, options=default_options)
        else:
            dag_sub = htcondor.Submit.from_dag(dag_file)

        clusterid, submit_result = condor_queue_job(dag_sub, schedd=schedd)
    except Exception as e:
        print(f'error submitting dag: {e}')
        clusterid = None
        submit_result = None
    return clusterid, submit_result


def condor_rm(spec, schedd):
    """
    Remove jobs from the HTCondor job queue based on the specified criteria.

    This function interacts with an HTCondor schedd (scheduler) to locate and
    remove jobs that match the provided specifications. Jobs can be queried
    either by their cluster ID or by their name, and the matching jobs will
    then be marked for removal from the job queue.

    :param spec: Criteria or specification to identify the jobs that should be
                 removed. This can be its cluster ID or job name used for
                 querying.
    :type spec: Any
    :param schedd: Identifier for the HTCondor scheduler where the jobs are
                   located. Defaults to the local scheduler if not provided.
    :type schedd: str|htcondor.Schedd | None

    :return: None
    """

    theschedd = get_schedd(schedd)

    res_list = query_by_clusterid(spec, schedd=theschedd)
    for res in res_list:
        job_id = res['ClusterId']
        theschedd.act(htcondor.JobAction.Remove, job_id)

    res_list = query_by_name(spec, schedd=theschedd)
    for res in res_list:
        job_id = res['ClusterId']
        theschedd.act(htcondor.JobAction.Remove, job_id)


def condor_get_held_jobs(constraint=None, projection=None, schedd=None):
    """
    Retrieve a list of held jobs from the HTCondor job queue based on the
    specified criteria.

    """
    default_constraint = 'JobStatus == 5'
    defaul_projection = ["Owner", "ClusterId", "ProcId", "JobBatchName", "JobStatus", "HoldReasonCode", "HoldReasonSubCode"
                         "NumJobStarts", "EnteredCurrentStatus", "HoldReason"]

    if constraint is None:
        constraint = default_constraint
    if projection is None:
        projection = defaul_projection

    ret = schedd_query(constraint=constraint, schedd=schedd, projection=projection)
    return ret


def condor_release_held_jobs(constraint=None, max_starts=3, wait=60, user_hold=False, schedd=None):
    """
    Releases held jobs in an HTCondor scheduler based on the reason code and subcode

    This function inspects held jobs in the HTCondor queue according to the input parameters
    and attempts to release them based on predefined criteria. Only jobs satisfying specific
    conditions are considered for release, and timing constraints are enforced to ensure that
    jobs are not prematurely released.

    :param constraint: A custom constraint used to filter held jobs. Defaults to all held jobs.
    :param max_starts: Maximum number of starts for a job before it isn't considered
        releasable. Defaults to 3.
    :param wait: Time (in seconds) to wait if a held job does not meet the minimum
        waiting time since its hold status was entered. Defaults to 60.
    :param user_hold: A boolean that specifies whether jobs held by 'user hold' should
        also be released. Defaults to False.
    :param schedd: Optional. Specifies a particular scheduler to retrieve jobs from.
        If not provided, the default scheduler is used.

    :return: None
    """
    user = getpass.getuser()
    releaseable_hold_reasons = {6: 7, 7: 2}
    if user_hold:
        releaseable_hold_reasons[1] = 0

    jobs = condor_get_held_jobs(constraint=constraint, schedd=schedd)
    if jobs:
        theschedd = get_schedd(schedd)
        for job in jobs:
            if job['HoldReasonCode'] in releaseable_hold_reasons.keys() and job['NumJobStarts'] < max_starts:
                if job['HoldReasonSubCode'] == releaseable_hold_reasons[job['HoldReasonCode']]:
                    hold_time = time() - job['EnteredCurrentStatus']
                    if hold_time < wait:
                        sleep(wait - hold_time)
                        job_id = job['ClusterId']
                        owner = job['Owner']
                        if owner == user:
                            theschedd.act(htcondor.JobAction.Release, job_id)
                        else:
                            print(f'Job {job_id} is held by {owner}, not {user}. If you have the privileges you could use:')
                            print(f'sudo -u {owner} condor_release {job_id}"')
