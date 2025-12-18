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
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
""""""

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'

import shutil
import socket
import tempfile
from pathlib import Path

import pytest
from htcondor2 import HTCondorException

from omicron_utils.condor_utils import get_schedd, condor_submit_job, wait_for_job, query_by_clusterid, \
    condor_submit_dag, condor_rm


class TestCondorUtils:

    @classmethod
    def setup_class(self):
        fqdn = socket.getfqdn()
        print(f'\nRunning tests on {fqdn} cwd: {Path.cwd()}')

        self.test_data_dir = Path('tests/test_data').absolute()
        self.sleep_submit = self.test_data_dir / 'sleep.submit'
        self.dag_submit = self.test_data_dir / 'sleep4.dag'
        self.dag_submit2 = self.test_data_dir / 'sleep2.dag'
        ok = True

        try:
            get_schedd()
        except HTCondorException as e:
            print(f'\nNo schedd found {e}: skipping test')
            ok = False
        for test_file in [self.sleep_submit, self.dag_submit, self.dag_submit2]:
            if not test_file.exists():
                print(f'Test file {test_file.absolute} does not exist')
                ok = False
        assert ok, 'No schedd available or test files missing'
        pass

    def test_condor_submit_job(self):

        my_fqdn = socket.getfqdn()
        print(f'\nMy FQDN: {my_fqdn}')
        run_test = True
        try:
            get_schedd()
        except HTCondorException as e:
            print(f'\nNo schedd found {e}: skipping test')
            run_test = False
        if run_test:
            with tempfile.TemporaryDirectory() as tmpdirname:
                print(f'\nTemporary directory created at: {tmpdirname}')
                sub_src = self.sleep_submit
                subfile = Path(tmpdirname) / sub_src.name
                shutil.copy(sub_src, subfile)
                print(f'Submit file: {subfile}')
                job_id, res = condor_submit_job(str(subfile.absolute()))
                print(f'Job ID: {job_id}')
                q_result = query_by_clusterid(job_id)
                print(f'Job {job_id} in queue: {q_result}')
                assert len(q_result) == 1
                assert job_id == q_result[0]['ClusterId']
                with pytest.raises(TimeoutError):
                    wait_for_job(job_id, timeout=10, sleep_time=2)
                print(f'{job_id}, appropriate timeout received´.')

                self.wait_for_it(job_id)
                print(f'Job {job_id} completed')

    def test_condor_submit_dag(self):

        my_fqdn = socket.getfqdn()
        print(f'\n FQDN: {my_fqdn}')

        run_test = True
        try:
            get_schedd()
        except HTCondorException as e:
            print(f'\nNo schedd found {e}: skipping test')
            run_test = False
        if run_test:
            with tempfile.TemporaryDirectory() as tmpdirname:
                print(f'\nTemporary directory created at: {tmpdirname}')
                sub_src = self.dag_submit
                subfile = Path(tmpdirname) / sub_src.name
                shutil.copy(sub_src, subfile)
                print(f'Submit file: {subfile}')
                job_id, res = condor_submit_dag(str(subfile.absolute()))
                print(f'Job ID: {job_id}')
                assert job_id is not None, "condor_submit_dag did not return a job ID"
                q_result = query_by_clusterid(job_id)
                print(f'Job {job_id} in queue: {q_result}')
                assert q_result is not None and len(q_result) > 0, 'Jo not found in queue'
                assert job_id == q_result[0]['ClusterId']
                with pytest.raises(TimeoutError):
                    wait_for_job(job_id, timeout=10, sleep_time=2)
                self.wait_for_it(job_id)
                print(f'Job {job_id} completed')

    def test_condor_submit_dag2(self):

        my_fqdn = socket.getfqdn()
        print(f'\n FQDN: {my_fqdn}')

        run_test = True
        try:
            get_schedd()
        except HTCondorException as e:
            print(f'\nNo schedd found {e}: skipping test')
            run_test = False
        if run_test:
            with tempfile.TemporaryDirectory() as tmpdirname:
                print(f'\nTemporary directory created at: {tmpdirname}')
                dag_sub_src = self.dag_submit2
                dag_subfile = Path(tmpdirname) / dag_sub_src.name
                shutil.copy(dag_sub_src, dag_subfile)
                print(f'DAG submit file: {dag_subfile}')
                job_sub_src = self.sleep_submit
                job_subfile = Path(tmpdirname) / job_sub_src.name
                shutil.copy(job_sub_src, job_subfile)
                print(f'Job submit file: {job_subfile}')
                job_id, res = condor_submit_dag(str(dag_subfile.absolute()))
                print(f'Job ID: {job_id}')
                assert job_id is not None, "condor_submit_dag did not return a job ID"
                q_result = query_by_clusterid(job_id)
                print(f'Job {job_id} in queue: {q_result}')
                assert q_result is not None and len(q_result) > 0, 'Jo not found in queue'
                assert job_id == q_result[0]['ClusterId']
                with pytest.raises(TimeoutError):
                    wait_for_job(job_id, timeout=10, sleep_time=2)
                self.wait_for_it(job_id)
                print(f'Job {job_id} completed')

    def wait_for_it(self, job_id, timeout=250, sleep_time=5):

        try:
            wait_for_job(job_id, timeout=timeout, sleep_time=sleep_time)
        except TimeoutError:
            condor_rm(job_id)
            pytest.fail(f'Job {job_id} did not complete in time')

    def test_release_held_jobs(self):
        pass
