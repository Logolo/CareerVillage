from cvt.commands import TargetRoleCommand
from fabric.api import sudo


class Command(TargetRoleCommand):

    help = 'sudo command runner'

    def register(self, parser):
        super(Command, self).register(parser)
        parser.add_argument('command', metavar='<command>')

    def apply(self, args):
        sudo(args.command)
