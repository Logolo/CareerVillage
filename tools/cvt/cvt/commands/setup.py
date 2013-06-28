from cvt.commands import BaseCommand
from cvt.common import get_instances, get_setting, get_settings
from fabric.api import run, sudo, env, put, local
from fabric.tasks import execute
import os


class Command(BaseCommand):

    help = 'setup a node'

    def register(self, parser):

        parser.set_defaults(handle=self.do)

        parser.add_argument('-r', '--role',
                            dest='role',
                            required=True,
                            help='role of the host')

        parser.add_argument('-t', '--target',
                            help='set target (local, pro)',
                            dest='target',
                            default='local')

        parser.add_argument('-e', '--reset-db',
                            help='run reset_db in the host (only for master)',
                            dest='reset_db',
                            action='store_true',
                            default=False)

        parser.add_argument('--host',
                            help='set host',
                            dest='host',
                            default=None)

        parser.add_argument('-m', '--manifest',
                            help='set manifest',
                            dest='manifest',
                            default=None)

    def do(self, args):
        target = args.target
        role = args.role
        manifest = args.manifest
        instances = get_instances(role=args.role, target=args.target)
        if args.host:
            instances = [i for i in instances if args.host in i.host]
        env.use_ssh_config = True
        setup_name = 'setup-{target}-{role}'.format(target=target, role=role)

        def get_instance(host):
            for i in instances:
                if host == i.host:
                    return i
            return None

        try:
            local('tar cf {setup_name}.tar  --exclude=.git -C {setup_dir} .'.format(
                setup_name=setup_name,
                setup_dir=get_setting('SETUP_DIR')))
            local('tar rf {setup_name}.tar -C {path} careervillage_{target}_git careervillage_{target}_git.pub'.format(
                path=get_setting('KEY_DIR'),
                setup_name=setup_name,
                target=target))
            local('gzip {setup_name}.tar'.format(setup_name=setup_name))

            def apply():
                instance = get_instance(env.host_string)

                if not os.path.isfile(os.path.abspath(os.path.join(get_setting('SETUP_DIR'), '{manifest}.pp'.format(manifest=manifest or instance.manifest)))):
                    print 'No manifest found: {manifest}.pp'.format(manifest=manifest or instance.manifest)
                    return

                put('{setup_name}.tar.gz'.format(setup_name=setup_name), '{setup_name}.tar.gz'.format(setup_name=setup_name))
                run('tar xzf {setup_name}.tar.gz'.format(setup_name=setup_name))
                sudo('mv careervillage_{target}_git /tmp/careervillage_git'.format(target=target))
                sudo('mv careervillage_{target}_git.pub /tmp/careervillage_git.pub'.format(target=target))

                #run this before installing puppet and git
                sudo('apt-get update')
                sudo('apt-get install puppet git -y')

                def convert(value):
                    #TODO: add support to other py types
                    if value is None:
                        value = '__NONE__'
                    elif value == '':
                        value = '__EMPTY__'
                    elif not isinstance(value, basestring):
                        value = str(value)
                    return '"{value}"'.format(value=value.replace('\"', '\\\"'))

                facts = ['export FACTER_careervillage_{name}={value};'.format(name=name.lower(), value=convert(value))
                         for name, value in get_settings('{target}_PUPPET'.format(target=target)).items()]
                facts.append('export FACTER_careervillage_target=\'{target}\';'.format(target=target))
                facts.append('export FACTER_careervillage_reset_db=\'{b}\';'.format(b=str(args.reset_db).lower()))

                sudo('{facts} puppet apply --debug --modulepath=modules {manifest}.pp'.format(
                    facts=''.join(facts),
                    manifest=manifest or instance.manifest))

            execute(apply, hosts=[i.host for i in instances])

        except Exception, e:
            print 'Error', e.message
        finally:
            if os.path.isfile('{setup_name}.tar.gz'.format(setup_name=setup_name)):
                local('rm {setup_name}.tar.gz'.format(setup_name=setup_name))
            if os.path.isfile('{setup_name}.tar'.format(setup_name=setup_name)):
                local('rm {setup_name}.tar'.format(setup_name=setup_name))
