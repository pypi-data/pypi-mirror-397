import logging
import os
import sys
import socket
import warnings
from datetime import datetime
from contextvars import ContextVar
from pathlib import Path

# Get hostname once at module load (first part only - e.g., 'taco.local' -> 'taco')
HOSTNAME = socket.gethostname().split('.')[0]

# Get version once at module load
try:
    # Path from src/lib/featrix/neural/logging_config.py to root VERSION file
    version_file = Path(__file__).parent.parent.parent.parent.parent / "VERSION"
    if version_file.exists():
        VERSION = version_file.read_text().strip()
    else:
        VERSION = "unknown"
except Exception:
    VERSION = "unknown"

# Flag to ensure logging is only configured once
_logging_configured = False

# Context variable to track current epoch across all threads/coroutines
current_epoch_ctx: ContextVar[int] = ContextVar('current_epoch', default=None)

# Context variable to track job prefix (e.g., job_id suffix, 'qa-credit-g', 'smoke', etc.)
job_prefix_ctx: ContextVar[str] = ContextVar('job_prefix', default=None)


class FeatrixFormatter(logging.Formatter):
    """
    Custom formatter for Featrix logging with standardized format:
    - Hostname and version shown FIRST: [hostname,version]
    - No year in timestamp, includes milliseconds
    - Log level ONLY for ERROR/WARNING (hidden for INFO/DEBUG)
    - Removes 'featrix.neural.' prefix from module names
    - Truncates module names to 16 chars max (single_predictor length) with middle ellipsis
    - Adds job_prefix context for identifying jobs across multiple windows
    - Shows epoch on EVERY line ([e=NNN] during training, 7 spaces otherwise) for vertical alignment and awk parsing
    """
    
    MAX_MODULE_WIDTH = 16  # Length of 'single_predictor'
    
    def formatTime(self, record, datefmt=None):
        """Format time without year, with milliseconds: MM-DD HH:MM:SS.mmm"""
        ct = self.converter(record.created)
        if datefmt:
            s = datetime.fromtimestamp(record.created).strftime(datefmt)
        else:
            # Default format: MM-DD HH:MM:SS.mmm
            s = f"{ct.tm_mon:02d}-{ct.tm_mday:02d} {ct.tm_hour:02d}:{ct.tm_min:02d}:{ct.tm_sec:02d}"
        # Add milliseconds
        s += f".{int(record.msecs):03d}"
        return s
    
    def _truncate_module_name(self, name: str) -> str:
        """
        Truncate module name to MAX_MODULE_WIDTH characters with middle ellipsis.
        Also removes 'featrix.neural.' prefix if present.
        
        Examples:
            'featrix.neural.embedded_space' -> 'embedded_space'
            'featrix.neural.input_data_set' -> 'input_data_set'
            'lib.featrix.neural.single_predictor' -> 'single_predictor'
            'very_long_module_name_that_exceeds_limit' -> 'very_lo…s_limit'
        """
        # Remove 'featrix.neural.' prefix if present
        if name.startswith('featrix.neural.'):
            name = name[15:]  # len('featrix.neural.') = 15
        
        # Take last component after final dot (if any)
        if '.' in name:
            name = name.split('.')[-1]
        
        # Truncate with middle ellipsis if needed
        if len(name) > self.MAX_MODULE_WIDTH:
            # Calculate how many chars to keep on each side
            # Leave 1 char for the ellipsis
            chars_available = self.MAX_MODULE_WIDTH - 1
            left_chars = chars_available // 2
            right_chars = chars_available - left_chars
            name = name[:left_chars] + '…' + name[-right_chars:]
        
        return name
    
    def format(self, record):
        # Always show epoch on EVERY line with fixed width [e=NNN] format (7 chars for awk parsing)
        if not hasattr(record, 'epoch_str'):
            epoch = current_epoch_ctx.get(None)
            if epoch is not None:
                # Format as [e=NNN] with 3 digits, zero-padded (7 chars: [e=001])
                record.epoch_str = f"[e={epoch:03d}]"
            else:
                # No epoch set - use 7 spaces to maintain column alignment for awk
                record.epoch_str = "       "
        
        # Add job_prefix if set
        if not hasattr(record, 'job_prefix_str'):
            job_prefix = job_prefix_ctx.get(None)
            if job_prefix is not None:
                record.job_prefix_str = f"[{job_prefix}] "
            else:
                record.job_prefix_str = ""
        
        # Conditional level string - only show for ERROR/WARNING
        if not hasattr(record, 'level_str'):
            if record.levelname in ('ERROR', 'WARNING'):
                record.level_str = f"[{record.levelname:<7s}] "
            else:
                # For INFO, DEBUG, etc. - show nothing
                record.level_str = ""
        
        # Truncate and clean module name
        module_name = record.name if hasattr(record, 'name') else 'root'
        record.short_name = self._truncate_module_name(module_name)
        
        return super().format(record)


class FeatrixFilter(logging.Filter):
    """Add current epoch, job prefix, and conditional level to log records."""
    def filter(self, record):
        # Always show epoch on EVERY line with fixed width [e=NNN] format (7 chars for awk parsing)
        if not hasattr(record, 'epoch_str'):
            epoch = current_epoch_ctx.get(None)
            if epoch is not None:
                # Format as [e=NNN] with 3 digits, zero-padded (7 chars: [e=001])
                record.epoch_str = f"[e={epoch:03d}]"
            else:
                # No epoch set - use 7 spaces to maintain column alignment for awk
                record.epoch_str = "       "
        
        # Always ensure job_prefix_str exists (even if not set by context)
        if not hasattr(record, 'job_prefix_str'):
            job_prefix = job_prefix_ctx.get(None)
            if job_prefix is not None:
                record.job_prefix_str = f"[{job_prefix}] "
            else:
                record.job_prefix_str = ""
        
        # Conditional level string - only show for ERROR/WARNING
        if not hasattr(record, 'level_str'):
            if record.levelname in ('ERROR', 'WARNING'):
                record.level_str = f"[{record.levelname:<7s}] "
            else:
                # For INFO, DEBUG, etc. - show nothing
                record.level_str = ""
        
        return True

def configure_logging(job_prefix: str = None):
    """
    Configure logging with standardized Featrix format for all processes.
    
    Standard format (hostname,version FIRST, no year, epoch on EVERY line):
        [hostname,version] MM-DD HH:MM:SS.mmm [job_prefix] [LEVEL] module [e=NNN]: message
    
    - Hostname and version shown FIRST for easy identification
    - Log level ONLY shown for ERROR/WARNING (hidden for INFO/DEBUG)
    - Epoch is ALWAYS shown ([e=001], [e=042], [e=999] during training, 7 spaces when not training for awk column alignment)
    - This ensures vertical alignment and makes it easy to identify training progress
    
    This should be called early in the process before any other modules
    that might call logging.basicConfig().
    
    Args:
        job_prefix: Optional job identifier (e.g., job_id suffix, 'qa-credit-g', 'smoke')
                   to help identify logs across multiple windows
    """
    global _logging_configured
    
    # Set job prefix in context if provided
    if job_prefix is not None:
        job_prefix_ctx.set(job_prefix)
    
    if _logging_configured:
        return
    
    # Get root logger once
    root_logger = logging.getLogger()
    
    # Force reconfiguration by clearing existing handlers
    root_logger.handlers = []
    
    # Set up standardized logging format:
    # - [hostname,version] FIRST for easy identification
    # - MM-DD HH:MM:SS.mmm (no year, with milliseconds)
    # - [job_prefix] optional job identifier
    # - [LEVEL] ONLY shown for ERROR/WARNING (hidden for INFO/DEBUG)
    # - [e=NNN] current epoch (ALWAYS shown, 7 spaces when not in training, fixed 7-char width for awk parsing)
    # - module name (max 16 chars, truncated with middle '…')
    # - message
    log_format = f'[{HOSTNAME},{VERSION}] %(asctime)s %(job_prefix_str)s%(level_str)s%(short_name)-16s %(epoch_str)s: %(message)s'
    formatter = FeatrixFormatter(log_format)
    
    # Create handler with our custom formatter (formatter ensures epoch_str exists)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    
    # Add Featrix filter to root logger as backup (formatter already handles it, but filter is extra safety)
    featrix_filter = FeatrixFilter()
    root_logger.addFilter(featrix_filter)
    
    # Also add filter to all existing handlers to ensure it's applied
    for handler in root_logger.handlers:
        if featrix_filter not in handler.filters:
            handler.addFilter(featrix_filter)
    
    # Also add to any child loggers that might have been created before this
    # This ensures all loggers get the epoch_str and job_prefix_str fields
    for logger_name in logging.Logger.manager.loggerDict:
        logger_obj = logging.getLogger(logger_name)
        if featrix_filter not in logger_obj.filters:
            logger_obj.addFilter(featrix_filter)
    
    _logging_configured = True
    
    # Suppress Pydantic protected namespace warnings (we've configured all models with protected_namespaces=())
    warnings.filterwarnings('ignore', message='.*Field.*has conflict with protected namespace.*model_.*', category=UserWarning)
    
    # Log that logging was configured (but use DEBUG level to avoid spam in INFO logs)
    # Workers spawn constantly and each one imports this module, causing log spam
    # 
    # CRITICAL: The PYTORCH_DATALOADER_WORKER env var is set in worker_init_fn, which runs
    # AFTER module imports. So we can't reliably detect workers at import time.
    # 
    # SOLUTION: Use DEBUG level for the configuration message so it doesn't spam INFO logs.
    # If you need to see it, set log level to DEBUG. This prevents spam from workers
    # that are constantly being spawned/recreated.
    logger = logging.getLogger(__name__)
    is_worker = os.environ.get('PYTORCH_DATALOADER_WORKER') == '1'
    
    # Use DEBUG level to avoid spam - workers spawn constantly and cause INFO log spam
    # Only use INFO level if we're definitely NOT a worker (env var check)
    if not is_worker:
        logger.debug(f"🕐 Featrix logging configured on {HOSTNAME}")
    # Workers: completely silent (DEBUG level) - no logging to avoid massive spam from constant respawning


def set_job_prefix(job_prefix: str):
    """
    Set the job prefix for the current context.
    
    This can be called at any time to change the job prefix for all subsequent logs.
    Useful for identifying jobs across multiple windows.
    
    Args:
        job_prefix: Job identifier (e.g., job_id suffix, 'qa-credit-g', 'smoke')
    """
    job_prefix_ctx.set(job_prefix)

# Auto-configure logging when this module is imported
configure_logging() 