import os
import logging
from logging.handlers import TimedRotatingFileHandler

def get_logger(
        logger_name: str = __name__,
        # path_base: str = config.storage_config.local_path_base
):
    # Create a custom logger
    logger = logging.getLogger(logger_name)
    
    # Create handlers
    c_handler = logging.StreamHandler()
    # f_handler = logging.FileHandler('file.log')
    c_handler.setLevel(logging.DEBUG)
    # f_handler.setLevel(logging.ERROR)
    
#     logger_path = os.path.join(path_base,"logs")
#     os.makedirs(logger_path, exist_ok=True)
    # Create a TimedRotatingFileHandler
    # f_handler = TimedRotatingFileHandler(ß
    #     filename=os.path.join(logger_path,"app.log"),       # Log file path
    #     when="midnight",               # Rotate at midnight
    #     interval=1,                    # Rotate every day
    #     backupCount=14,                 # Keep 7 days of logs
    #     encoding="utf-8"
    # )
    
    # Optional: Set file suffix to include date
    # f_handler.suffix = "%Y-%m-%d"
    
    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(levelname)s - %(name)s:%(lineno)d - %(message)s')
    f_format = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s:%(lineno)d - %(message)s')
    c_handler.setFormatter(c_format)
    # f_handler.setFormatter(f_format)
    
    # Add handlers to the logger
    logger.addHandler(c_handler)
    # logger.addHandler(f_handler)
    
    logger.setLevel(logging.DEBUG)  # Set the logger to debug level
    # logger.warning('This is a warning')
    # logger.error('This is an error')
    return logger