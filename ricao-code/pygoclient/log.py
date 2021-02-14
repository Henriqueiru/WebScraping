from logging import info, error, warning, basicConfig, INFO, ERROR, WARNING

from colorama import Back, Fore, Style, init
init(autoreset=True)

format = "[%(asctime)s.%(msecs)03d]%(message)s"
datefmt = "%H:%M:%S"

#We will not use a status for 'Submitting' as this it pointless imo
statuses = {
    'INITIALIZING': Fore.MAGENTA, #Starting tasks
    'WAITING': Fore.YELLOW, #Waiting in queue, waiting for captcha
    'FINISHED' : Fore.CYAN, #Finished a stage, E.G. Submitted Shipping
    'SUCCESS': Fore.GREEN, #Checkout, ATC, Bypass
    'FAILED': Fore.RED #Failed a stage, any error
}

def log_status(msg, status, module, task_id):
    basicConfig(format=format, level=INFO, datefmt=datefmt)
    info(statuses[status] + f"[{module}][{task_id}] {msg}")

def log_info(msg: str, title=None): #Make redundant soon
    return #Enable for request debugging, refer to sockets -> request for further logging
    basicConfig(format=format, level=INFO, datefmt=datefmt)
    info(f"[info{(' - ' + title) if title is not None else ''}] " + msg)


def log_error(msg: str, title=None): #Make redundant soon
    basicConfig(format=format, level=ERROR, datefmt=datefmt)
    error(f"[error{(' - ' + title) if title is not None else ''}] " + msg)


def log_warning(msg: str, title=None): #Make redundant soon
    basicConfig(format=format, level=WARNING, datefmt=datefmt)
    warning(f"[warning{(' - ' + title) if title is not None else ''}] " + msg)
