class TaskManagerBusy(Exception):
    def __init__(self):
        super().__init__('TaskManager is busy')

class TaskManagerOff(Exception):
    def __init__(self):
        super().__init__('TaskManager is off') 