import logging
from argparse import Action, ArgumentParser


log = logging.getLogger()


class IntChoiceAction(Action):
    def __init__(self, option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):
        super(IntChoiceAction, self).__init__(option_strings,
                                              dest,
                                              nargs,
                                              const,
                                              default,
                                              type,
                                              choices,
                                              required,
                                              help,
                                              metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.choices[values])


def logger_action(parser: ArgumentParser):
    parser.add_argument('-l', '--log-level', dest='log_level', choices={
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARN': logging.WARNING,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET,
    }, action=IntChoiceAction)
