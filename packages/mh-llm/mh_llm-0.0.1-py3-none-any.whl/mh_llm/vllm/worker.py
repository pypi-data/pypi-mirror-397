from vllm.v1.worker.gpu_worker import Worker as GPUWorker
from .model_runner import GPUModelRunner

from .utils import patch as mh_patch


class Worker(GPUWorker):

  def init_device(self):
    with mh_patch([{
        'module': 'vllm.v1.worker.gpu_worker',
        'class': GPUModelRunner,
        'new_class': GPUModelRunner,
    }]):
      super().init_device()
