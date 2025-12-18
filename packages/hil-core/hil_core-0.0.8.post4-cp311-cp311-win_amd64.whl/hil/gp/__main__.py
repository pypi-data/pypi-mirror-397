from .bin import main
from loguru import logger


logger.enable("hil.gp")
main()