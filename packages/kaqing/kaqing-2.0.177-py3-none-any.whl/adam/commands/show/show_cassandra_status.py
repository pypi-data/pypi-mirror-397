import sys

from adam.checks.check_result import CheckResult
from adam.checks.check_utils import run_checks
from adam.checks.compactionstats import CompactionStats
from adam.checks.gossip import Gossip
from adam.columns.columns import Columns
from adam.commands import extract_options
from adam.commands.command import Command
from adam.commands.cql.utils_cql import cassandra
from adam.config import Config
from adam.utils_issues import IssuesUtils
from adam.utils_k8s.statefulsets import StatefulSets
from adam.repl_state import ReplState, RequiredState
from adam.utils import SORT, tabulize, log, log2, log_exc
from adam.checks.status import parse_nodetool_status

class ShowCassandraStatus(Command):
    COMMAND = 'show cassandra status'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ShowCassandraStatus, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ShowCassandraStatus.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validate(args, state) as (args, state):
            with extract_options(args, ['-s', '--show']) as (args, show_out):
                if state.namespace and state.pod:
                    self.show_single_pod(state, show_out=show_out)
                elif state.namespace and state.sts:
                    self.merge(state, Config().get('nodetool.samples', sys.maxsize), show_output=show_out)

                return state

    def show_single_pod(self, state: ReplState, show_out = False):
        with log_exc(True):
            with cassandra(state) as pods:
                result = pods.nodetool('status', show_out=False)
                status = parse_nodetool_status(result.stdout)
                check_results = run_checks(cluster=state.sts, namespace=state.namespace, checks=[CompactionStats(), Gossip()], show_out=show_out)
                self.show_table(status, check_results)

    def merge(self, state: ReplState, samples: int, show_output=False):
        statuses: list[list[dict]] = []

        pod_names = StatefulSets.pod_names(state.sts, state.namespace)
        for pod_name in pod_names:
            pod_name = pod_name.split('(')[0]

            with log_exc(True):
                with cassandra(state, pod=pod_name) as pods:
                    result = pods.nodetool('status', show_out=False)
                    status = parse_nodetool_status(result.stdout)
                    if status:
                        statuses.append(status)
                    if samples <= len(statuses) and len(pod_names) != len(statuses):
                        break

        combined_status = self.merge_status(statuses)
        log2(f'Showing merged status from {len(statuses)}/{len(pod_names)} nodes...')
        check_results = run_checks(cluster=state.sts, namespace=state.namespace, checks=[CompactionStats(), Gossip()], show_out=show_output)
        self.show_table(combined_status, check_results)

        return combined_status

    def merge_status(self, statuses: list[list[dict]]):
        combined = statuses[0]

        status_by_host = {}
        for status in statuses[0]:
            status_by_host[status['host_id']] = status
        for status in statuses[1:]:
            for s in status:
                if s['host_id'] in status_by_host:
                    c = status_by_host[s['host_id']]
                    if c['status'] == 'UN' and s['status'] == 'DN':
                        c['status'] = 'DN*'
                else:
                    combined.append(s)

        return combined

    def show_table(self, status: list[dict[str, any]], check_results: list[CheckResult]):
        cols = Config().get('status.columns', 'status,address,load,tokens,owns,host_id,gossip,compactions')
        header = Config().get('status.header', '--,Address,Load,Tokens,Owns,Host ID,GOSSIP,COMPACTIONS')
        columns = Columns.create_columns(cols)

        tabulize(status, lambda s: ','.join([c.host_value(check_results, s) for c in columns]), header=header, separator=',', sorted=SORT)

        IssuesUtils.show(check_results)

    def completion(self, state: ReplState):
        return super().completion(state, {'-s': None})

    def help(self, _: ReplState):
        return f'{ShowCassandraStatus.COMMAND} [-s]\t show merged nodetool status  -s show commands on nodes'