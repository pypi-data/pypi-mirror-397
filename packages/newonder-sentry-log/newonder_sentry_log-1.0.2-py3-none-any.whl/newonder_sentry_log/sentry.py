import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import sentry_sdk
from sentry_sdk import set_tag, set_user, capture_exception
from sentry_sdk.integrations.logging import LoggingIntegration
import os

class NewonderLog(object):
    """A logging utility that integrates with Sentry and supports local file logging."""
    
    # Programme identifier
    PROGRAMME = 'NewonderLog'
    # Version of the logging system
    VERSION = '1.0.2'

    def __init__(self, project_name, project_version, author, set_level='work',
                 sentry_url=None, email_domain=None, log_path=None,
                 file_name=None, err_name=None,
                 log_level=logging.INFO, error_log_level=logging.ERROR
                 ):
        """
        Initialize the NewonderLog instance.
        
        Args:
            project_name (str): Name of the project using this logger
            project_version (str): Version of the project
            author (str): Author of the project
            set_level (str): Log level ('work' for production, other values for development)
            sentry_url (str, optional): Sentry DSN URL for error reporting
            email_domain (str, optional): Email domain for user identification
            log_path (str, optional): Custom path for log files, defaults to ../log relative to this file
            file_name (str, optional): Base name for the info log file
            err_name (str, optional): Base name for the error log file
            log_level: Minimum level for info logs (default: logging.INFO)
            error_log_level: Minimum level for error logs (default: logging.ERROR)
        """
        self.project_name = project_name
        self.project_version = project_version
        self.author = author
        self.set_level = str(set_level)
        self.sentry_url = sentry_url
        self.email_domain = email_domain or "xinhuadu.com.cn"
        
        # Create log directory
        self.log_path = log_path or os.path.join(os.path.dirname(__file__), "/var/log")
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        
        # Initialize logger
        self.logger = logging.getLogger(f"{project_name}_logger")
        self.logger.setLevel(log_level)
        self.logger.propagate = False
        
        # Clear existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Configure Sentry integration if in work mode and URL is provided
        if set_level == 'work' and sentry_url:
            # Configure Sentry for exception logging
            sentry_logging = LoggingIntegration(
                level=logging.INFO,        # Capture INFO+ logs as breadcrumbs
                event_level=error_log_level  # Send ERROR+ logs as events
            )
            sentry_sdk.init(
                dsn=sentry_url,
                integrations=[sentry_logging],
                traces_sample_rate=1.0
            )
            email = "{}@{}".format(self.author, self.email_domain)
            set_user({"email": email, "username": self.author})
            set_tag("func_name", project_name)
            
            # Configure local file logging
            self._setup_local_logging(self.log_path, file_name, err_name, log_level, error_log_level)
    
    def _setup_local_logging(self, log_path, file_name, err_name, log_level, error_log_level):
        """
        Configure local file logging.
        
        Args:
            log_path (str): Path to the log directory
            file_name (str): Base name for the info log file
            err_name (str): Base name for the error log file
            log_level: Minimum level for info logs
            error_log_level: Minimum level for error logs
        """
        # Log format
        fmt = logging.Formatter(
            '[%(asctime)s][%(filename)s][line:%(lineno)d][%(levelname)s]: %(message)s',
            '%Y-%m-%d %H:%M:%S')
        
        # Console output (for debugging only)
        # sh = logging.StreamHandler()
        # sh.setFormatter(fmt)
        # sh.setLevel(logging.DEBUG)
        # self.logger.addHandler(sh)
        
        # Info log file with daily rotation, kept for 14 days
        if file_name is not None:
            info_handler = TimedRotatingFileHandler(
                os.path.join(log_path, file_name + ".log"),
                when='D',
                backupCount=14,
                encoding='utf-8'
            )
            info_handler.suffix = "%Y-%m-%d"
            info_handler.setFormatter(fmt)
            info_handler.setLevel(log_level)
            # Only log INFO to WARNING level messages
            info_handler.addFilter(lambda record: record.levelno < error_log_level)
            self.logger.addHandler(info_handler)
        
        # Error log file with size-based rotation
        if err_name is not None:
            err_handler = RotatingFileHandler(
                os.path.join(log_path, err_name + ".log"),
                mode='a',
                maxBytes=100 * 1024 * 1024,  # 100MB
                backupCount=5,
                encoding='utf-8'
            )
            err_handler.setFormatter(fmt)
            err_handler.setLevel(error_log_level)
            self.logger.addHandler(err_handler)

    def _prepare_extra(self, log_str, farm=None, turbine=None, func_name=None, extra={}):
        """
        Prepare additional log information.
        
        Args:
            log_str (str): The log message
            farm (str, optional): Farm identifier
            turbine (str, optional): Turbine identifier
            func_name (str, optional): Function name
            extra (dict): Additional custom fields
            
        Returns:
            dict: Prepared extra information for logging
        """
        need_extra = {
            'func_status': "Info", 
            'farm': farm, 
            'turbine': turbine, 
            'func_name': func_name,
            'project_name': self.project_name, 
            'func_version': self.project_version, 
            'author': self.author
        }
        need_extra.update(extra)
        
        # Handle special field name conflicts
        if 'date' in need_extra:
            need_extra['self_date'] = need_extra.pop('date')
        if 'paramater' in need_extra and 'date' in need_extra['paramater']:
            need_extra['paramater']['file_date'] = need_extra['paramater'].pop('date')
            
        return need_extra

    def info(self, log_str, farm=None, turbine=None, func_name=None, extra={}):
        """
        Log an info message.
        
        Args:
            log_str (str): The log message
            farm (str, optional): Farm identifier
            turbine (str, optional): Turbine identifier
            func_name (str, optional): Function name
            extra (dict): Additional custom fields
        """
        need_extra = self._prepare_extra(log_str, farm, turbine, func_name, extra)
        
        if self.set_level != 'work':
            need_extra['message'] = log_str
            print(need_extra)
        else:
            self.logger.info(log_str, extra=need_extra)

    def debug(self, log_str, farm=None, turbine=None, func_name=None, extra={}):
        """
        Log a debug message.
        
        Args:
            log_str (str): The log message
            farm (str, optional): Farm identifier
            turbine (str, optional): Turbine identifier
            func_name (str, optional): Function name
            extra (dict): Additional custom fields
        """
        need_extra = self._prepare_extra(log_str, farm, turbine, func_name, extra)
        
        if self.set_level != 'work':
            need_extra['message'] = log_str
            print(need_extra)
        else:
            self.logger.debug(log_str, extra=need_extra)

    def warning(self, log_str, farm=None, turbine=None, func_name=None, extra={}):
        """
        Log a warning message.
        
        Args:
            log_str (str): The log message
            farm (str, optional): Farm identifier
            turbine (str, optional): Turbine identifier
            func_name (str, optional): Function name
            extra (dict): Additional custom fields
        """
        need_extra = self._prepare_extra(log_str, farm, turbine, func_name, extra)
        need_extra['func_status'] = "Warning"
        
        if self.set_level != 'work':
            need_extra['message'] = log_str
            print(need_extra)
        else:
            self.logger.warning(log_str, extra=need_extra)

    def error(self, log_str, farm=None, turbine=None, func_name=None, extra={}):
        """
        Log an error message.
        
        Args:
            log_str (str): The log message
            farm (str, optional): Farm identifier
            turbine (str, optional): Turbine identifier
            func_name (str, optional): Function name
            extra (dict): Additional custom fields
        """
        need_extra = self._prepare_extra(log_str, farm, turbine, func_name, extra)
        need_extra['func_status'] = "Error"
        
        if self.set_level != 'work':
            need_extra['message'] = log_str
            print(need_extra)
        else:
            self.logger.error(log_str, extra=need_extra)

    def exception(self, log_str, farm=None, turbine=None, func_name=None, extra={}):
        """
        Log an exception message and send to Sentry.
        
        Args:
            log_str (str): The log message
            farm (str, optional): Farm identifier
            turbine (str, optional): Turbine identifier
            func_name (str, optional): Function name
            extra (dict): Additional custom fields
        """
        need_extra = self._prepare_extra(log_str, farm, turbine, func_name, extra)
        need_extra['func_status'] = "Exception"
        
        if self.set_level != 'work':
            need_extra['message'] = log_str
            print(need_extra)
        else:
            self.logger.error(log_str, extra=need_extra)
            capture_exception()