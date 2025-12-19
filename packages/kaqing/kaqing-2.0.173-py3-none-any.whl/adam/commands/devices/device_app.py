from adam.apps import Apps
from adam.commands import app
from adam.commands.bash.bash_completer import BashCompleter
from adam.commands.command import Command, InvalidStateException
from adam.commands.devices.device import Device
from adam.config import Config
from adam.repl_state import ReplState
from adam.utils import lines_to_tabular, log, wait_log
from adam.utils_k8s.app_pods import AppPods
from adam.utils_k8s.ingresses import Ingresses

class DeviceApp(Command, Device):
    COMMAND = f'{ReplState.A}:'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(DeviceApp, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return DeviceApp.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not self.args(cmd):
            return super().run(cmd, state)

        state.device = ReplState.A

        return state

    def completion(self, state: ReplState):
        return super().completion(state)

    def help(self, _: ReplState):
        return f'{DeviceApp.COMMAND}\t move to App Operations device'

    def ls(self, cmd: str, state: ReplState):
        if state.app_pod:
            return self.bash(state, state, cmd.split(' '))
        elif state.app_app:
            pods = AppPods.pod_names(state.namespace, state.app_env, state.app_app)

            log(lines_to_tabular(pods, 'POD_NAME'))
        elif state.app_env:
            def line(n: str, ns: str):
                host = Ingresses.get_host(Config().get('app.login.ingress', '{app_id}-k8singr-appleader-001').replace('{app_id}', f'{ns}-{n}'), ns)
                if not host:
                    return None

                endpoint = Config().get('app.login.url', 'https://{host}/{env}/{app}').replace('{host}', host).replace('{env}', state.app_env).replace('{app}', 'c3')
                if not endpoint:
                    return None

                return f"{n.split('-')[1]},{Ingresses.get_host(f'{ns}-{n}-k8singr-appleader-001', ns)},{endpoint}"

            svcs = [l for l in [line(n, ns) for n, ns in Apps.apps(state.app_env)] if l]

            log(lines_to_tabular(svcs, 'APP,HOST,ENDPOINT', separator=','))
        else:
            svcs = [n for n, ns in Apps.envs()]

            log(lines_to_tabular(svcs, 'ENV', separator=','))

    def ls_completion(self, cmd, state, default: dict = {}):
        if state.app_app:
            def pod_names():
                return [p for p in AppPods.pod_names(state.namespace, state.app_env, state.app_app)]

            return super().completion(state) | {f'@{p}': {cmd: None} for p in pod_names()}

        return default

    def cat(self, cmd: str, state: ReplState):
        if state.app_pod:
            return self.bash(state, state, cmd.split(' '))

        raise InvalidStateException()

    def cat_completion(self, cmd: str, state: ReplState, default: dict = {}):
        if state.app_app:
            return {f'@{p}': {cmd: None} for p in AppPods.pod_names(state.namespace, state.app_env, state.app_app)}

        return default

    def cd(self, dir: str, state: ReplState):
        if dir == '':
            state.app_env = None
            state.app_app = None
            state.app_pod = None
        elif dir == '..':
            if state.app_pod:
                state.app_pod = None
            elif state.app_app:
                state.app_app = None
            else:
                state.app_env = None
        else:
            if state.app_app:
                state.app_pod = dir
            elif not state.app_env:
                tks = dir.split('@')
                if len(tks) > 1:
                    state.namespace = tks[1]

                state.app_env = dir.split('@')[0]
            else:
                state.app_app = dir

    def cd_completion(self, cmd: str, state: ReplState, default: dict = {}):
        if state.app_app:
            return {cmd: {'..': None} | {pod: None for pod in AppPods.pod_names(state.namespace, state.app_env, state.app_app)}}
        elif state.app_env:
            return {cmd: {'..': None} | {app[0].split('-')[1]: None for app in Apps.apps(state.app_env)}}
        else:
            return {cmd: {'..': None} | {env[0]: None for env in Apps.envs()}}

    def pwd(self, state: ReplState):
        words = []

        if state.app_env:
            words.append(f'env/{state.app_env}')
        if state.app_app:
            words.append(f'app/{state.app_app}')

        return '\t'.join([f'{ReplState.X}:>'] + (words if words else ['/']))

    def try_fallback_action(self, chain: Command, state: ReplState, cmd: str):
        if state.app_app:
            return True, chain.run(f'app {cmd}', state)

        return False, None

    def enter(self, state: ReplState):
        if not state.app_env:
            if auto_enter := Config().get('repl.a.auto-enter', 'c3/c3/*'):
                if auto_enter != 'no':
                    ea = auto_enter.split('/')
                    state.app_env = ea[0]
                    if len(ea) > 2:
                        state.app_app = ea[1]
                        state.app_pod = ea[2]
                        if state.app_pod == '*':
                            if (pods := AppPods.pod_names(state.namespace, ea[0], ea[1])):
                                state.app_pod = pods[0]
                                wait_log(f'Moving to {state.app_env}/{state.app_app}/{state.app_pod}...')
                            else:
                                wait_log(f'No pods found, moving to {state.app_env}/{state.app_app}...')
                        else:
                            wait_log(f'Moving to {state.app_env}/{state.app_app}/{state.app_pod}...')
                    elif len(ea) > 1:
                        state.app_app = ea[1]
                        wait_log(f'Moving to {state.app_env}/{state.app_app}...')
                    else:
                        wait_log(f'Moving to {state.app_env}...')

    def bash_target_changed(self, s0: ReplState, s1: ReplState):
        return s0.app_env != s1.app_env or s0.app_app != s1.app_app or s0.app_pod != s1.app_pod

    def exec_no_dir(self, command: str, state: ReplState):
        with app(state) as pods:
            return pods.exec(command)

    def exec_with_dir(self, command: str, session_just_created: bool, state: ReplState):
        with app(state) as pods:
            return pods.exec(command, not session_just_created)

    def bash_completion(self, cmd: str, state: ReplState, default: dict = {}):
        return {cmd: BashCompleter(lambda: [])} | \
               {f'@{p}': {cmd: BashCompleter(lambda: [])} for p in AppPods.pod_names(state.namespace, state.app_env, state.app_app)}