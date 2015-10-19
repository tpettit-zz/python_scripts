#! /usr/bin/python3.4
"""
Computer setup script
"""
import logging

import os
from os import system

from shlex import quote
from computer_config import config
from shutil import copy2 as copy
from util.logging import setup_logger


class Machine(object):
    def __init__(self, host, laptop, desktop, home, bashrc, git, **kwargs):
        log.info('Initializing Machine: %s', host)
        log.debug('laptop=%s, desktop=%s, home=%s, bashrc=%s, git=%s',
                  laptop, desktop, home, bashrc, git)
        self.host = host
        self.laptop = laptop
        self.desktop = desktop
        self.home = home
        self.bashrc = bashrc
        self.git = git

        for k, v in kwargs.items():
            log.debug('Arg: %s = %s', k, v)
            setattr(self, k, v)

    def setup(self):
        log.info('Setting Up: %s', self.host)
        self.write_bashrc()
        self.write_git_config()

    def send_file(self, src, dest):
        copy(src, dest)

    def run_command(self, cmd):
        system('bash -c {}'.format(quote(cmd)))

    def write_bashrc(self):
        log.info('Writing %s', self.bashrc)
        tmp_out = self.host + '.bashrc'
        with open(tmp_out, 'w') as out:
            out.write(config['bashrc'].substitute(**self.__dict__))
        self.send_file(tmp_out, self.bashrc)
        os.remove(tmp_out)

    def _flatten_config(self, d=config['git']):
        res = []
        for k, v in d.items():
            if type(v) is dict:
                for sub_key, val in self._flatten_config(v):
                    res.append((k + '.' + sub_key, val))
            else:
                res.append((k, v))
        return res

    def write_git_config(self):
        log.info('Configuring git')
        cmds = []
        for k, v in self._flatten_config():
            log.debug('git config: %s = %s', k, v)
            cmds.append('{} config --global --add {} "{}"'.format(self.git, k, v))

        self.run_command('; '.join(cmds))


class RemoteMachine(Machine):
    def __init__(self, **kwargs):
        super(RemoteMachine, self).__init__(**kwargs)
        init_cmds = '; '.join([
            'ssh -t {host} "sudo mkdir -p {home}',
            'sudo chown -R timothp:amazon {home}"'
        ]).format(**self.__dict__)

        system(init_cmds)

    def send_file(self, src, dest):
        system('scp {} {}:{}'.format(quote(src), self.host, quote(dest)))

    def run_command(self, cmd):
        system('ssh {} {}'.format(self.host, quote(cmd)))


if __name__ == "__main__":
    import argparse
    from util.cmdline_options import logger_action

    parser = argparse.ArgumentParser(description='Setup Computer')
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true')
    logger_action(parser)
    args = parser.parse_args()

    log = setup_logger('setup_computer', args.log_level if args.log_level is not None else logging.WARNING)

    if args.dry_run:
        def dry_copy(src, dest):
            log.info('Copy {} -> {}'.format(src, dest))
        copy = dry_copy

        def dry_system(cmd):
            log.info('Running: {}'.format(cmd))
        system = dry_system

    DESKTOP = RemoteMachine(dry_run=args.dry_run, **config['desktop'])
    LAPTOP = Machine(dry_run=args.dry_run, **config['laptop'])

    DESKTOP.setup()
    LAPTOP.setup()
