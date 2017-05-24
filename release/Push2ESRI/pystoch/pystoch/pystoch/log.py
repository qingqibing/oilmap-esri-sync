import logging
import sys

class ConsoleHandler(logging.StreamHandler):

    def flush(self):
        if self.stream and hasattr(self.stream, 'flush') and not self.stream.closed:
            # Can't use super because logging.Streamhandler is not new style class
            logging.StreamHandler.flush(self)

def set_logging(rank, size):
    # create logger with 'spam_application'
    logger = logging.getLogger('pystoch')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('C:\\TEMP\\pystoch_%d_of_%d.log' % (rank+1, size), mode='w')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = ConsoleHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    if rank == 0:
        logger.addHandler(ch)
    
    return logger
