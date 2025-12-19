import functools
import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("large_scale_deployer.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("large_scale_deployer")


def process_output(success_code=0, fail_code=-1, exceptions=(BaseException,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cmd = ' '.join(sys.argv[1:])
            return_code = success_code
            try:
                func(*args, **kwargs)
                logger.info(f"run cmd: {cmd} successfully.{os.linesep}")
            except KeyboardInterrupt:  # handle KeyboardInterrupt
                return_code = fail_code
                logger.warning(f"User interrupted the program by Keyboard.{os.linesep}")
            except SystemExit as e:
                if e.code == 0:
                    return_code = success_code
                    logger.info(f"run cmd: {cmd} successfully.{os.linesep}")
                else:
                    return_code = fail_code
                    logger.error(f"run cmd: {cmd} failed, reason: {str(e)}.{os.linesep}")
            except exceptions as e:
                return_code = fail_code
                logger.error(f"run cmd: {cmd} failed, reason: {str(e)}.{os.linesep}")
            sys.exit(return_code)

        return wrapper

    return decorator
