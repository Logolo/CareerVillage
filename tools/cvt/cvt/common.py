from cvt.conf import settings
import boto
import boto.ec2
from instances import VagrantInstance, EC2Instance


local_instances = [
    VagrantInstance('master', '10.0.1.10'),
]


def ec2_connection():
    return boto.ec2.connection.EC2Connection(
        settings.AWS_ACCESS_KEY_ID,
        settings.AWS_SECRET_ACCESS_KEY
    )


def ec2_instances():
    return [EC2Instance(i) for r in ec2_connection().get_all_instances()
            for i in r.instances if i.state == u'running']


def get_instances(target, role=None):
    instances = local_instances if target == 'local' else ec2_instances()
    return [i for i in instances if i.target == target and (role is None or role == i.role)]


def get_settings(prefix=None):
    return dict([((prefix and v[len(prefix)+1:]) or v, getattr(settings, v),)
                 for v in dir(settings)
                 if not v.startswith('__') and (prefix is None or v.lower().startswith(prefix.lower()))])


def get_setting(key, target=None, default=None):
    if target:
        return getattr(settings, target.upper() + '_' + key.upper(), default)
    else:
        return getattr(settings, key.upper(), default)