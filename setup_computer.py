#! /usr/bin/env python3
"""
Computer setup script
"""
import logging

import os
from os import system, path

from shlex import quote
from computer_config import config
from shutil import copy2 as copy
from util.logging import setup_logger


class Machine(object):
    @classmethod
    def dry_run(cls):
        def dry_send_file(self, src, dest):
            log.info('Copy {} -> {}'.format(src, dest))

        cls.send_file = dry_send_file

        def dry_run_command(self, cmd):
            log.info('Running: {}'.format(cmd))

        cls.run_command = dry_run_command

    def __init__(self, dry_run, host, laptop, desktop, home, bashrc, git, **kwargs):
        log.info('Initializing Machine: %s', host)
        log.debug('laptop=%s, desktop=%s, home=%s, bashrc=%s, git=%s',
                  laptop, desktop, home, bashrc, git)
        self.host = host
        self.laptop = laptop
        self.desktop = desktop
        self.home = home
        self.bashrc = bashrc
        self.git = git

        self.dry_run = dry_run

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
        out_file = ''
        if type(self.bashrc) is str:
            out_file = path.join(self.home, self.bashrc)
        else:
            out_file = path.join(self.home, self.bashrc['name'])

        log.info('Writing %s', out_file)
        tmp_out = self.host + '.bashrc'

        with open(tmp_out, 'w') as out:
            if type(self.bashrc) is dict:
                if 'pre_tmpl' in self.bashrc:
                    out.write(self.bashrc['pre_tmpl'].substitute(**self.__dict__))

            out.write(config['bashrc'].substitute(**self.__dict__))

            if type(self.bashrc) is dict:
                if 'post_tmpl' in self.bashrc:
                    out.write(self.bashrc['post_tmpl'].substitute(**self.__dict__))

        self.send_file(tmp_out, out_file)
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

        self.run_command(init_cmds)

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
        Machine.dry_run()
        RemoteMachine.dry_run()

    DESKTOP = RemoteMachine(dry_run=args.dry_run, **config['desktop'])
    LAPTOP = Machine(dry_run=args.dry_run, **config['laptop'])

    DESKTOP.setup()
    LAPTOP.setup()
