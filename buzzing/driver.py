import logging

def main():
    setup_logger()
    log = logging.getLogger(__name__)
    log.info("Welcome to Buzzing!")

def setup_logger():
    log_formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-13.13s] [%(levelname)-5.5s]  %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)
    file_handler = logging.FileHandler("buzzing.log")
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

if __name__ == "__main__":
    main()
