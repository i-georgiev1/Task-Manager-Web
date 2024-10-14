class Task:
    _id_counter = 1

    def __init__(self, description='', priority='', status=False, due_date=None, notified='no'):
        self.id = Task._id_counter
        Task._id_counter += 1
        self.description = description
        self.priority = priority
        self.status = status
        self.due_date = due_date
        self.notified = notified

    def __str__(self):
        is_completed = "Завършена" if self.status else "Незавършена"
        return f"Задача {self.id}: {self.description} с приоритет {self.priority} е {is_completed} (Срок: {self.due_date})"
