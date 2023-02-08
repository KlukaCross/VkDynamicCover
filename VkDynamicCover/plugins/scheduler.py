from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR


class _Scheduler(BackgroundScheduler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._jobs_queue = []
        self._jobs = []
        self.add_listener(self.error_listener, EVENT_JOB_ERROR)

    def error_listener(self, event):
        if event.exception:
            self.stop()

    def stop(self):
        if self.running:
            self.shutdown(wait=False)

    def add_job(self, *args, **kwargs):
        self._jobs_queue.append((args, kwargs))

    def start(self, *args, **kwargs):
        for j_args, j_kwargs in self._jobs_queue:
            self._jobs.append(super().add_job(*j_args, **j_kwargs))
        self._jobs_queue.clear()
        super().start(*args, **kwargs)


Scheduler = _Scheduler()
