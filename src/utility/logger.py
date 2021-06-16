import logging
from datetime import datetime

def create_logger(path):
    """Creates a logger and logging file it logs into

    Args:
        path (Str): Path to the log
    """
    today = datetime.now().strftime("%Y-%b-%d-%H-%M")
    logname = "{}/{}.log".format(path, today) 
    # creating log file and naming the logger
    logging.basicConfig(filename=logname,
                        format="%(asctime)s | %(levelname)s: %(message)s",
                        datefmt="%m/%d/%Y %I:%M:%S",
                        filemode="a",
                        level=logging.DEBUG)