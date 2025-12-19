#import logging
#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.DEBUG)

from ipykernel.kernelapp import IPKernelApp
from .kernel import MicroPythonExtendedKernel
IPKernelApp.launch_instance(kernel_class=MicroPythonExtendedKernel)

