from ipykernel.kernelapp import IPKernelApp
from . import RudiKernel


IPKernelApp.launch_instance(kernel_class=RudiKernel)
