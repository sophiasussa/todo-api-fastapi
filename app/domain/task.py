class Task:
    def __init__(self, id: int, title: str, done: bool = False):
        self.id = id
        self.title = title
        self.done = done

    def complete(self):
        if self.done:
            raise ValueError("Task already completed")
        self.done = True
