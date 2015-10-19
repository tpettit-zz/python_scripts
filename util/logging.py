import logging


def setup_logger(app, level):
    log = logging.getLogger()
    log.setLevel(level)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('{}.log'.format(app))
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    log.addHandler(fh)
    log.addHandler(ch)

    return logging.getLogger(app)
