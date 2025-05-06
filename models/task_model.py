from bson import ObjectId

class TaskModel:
    def __init__(self, mongo):
        self.tasks = mongo.db.tasks

    def add_task(self, username, task_text):
        self.tasks.insert_one({
            "username": username,
            "task": task_text,
            "completed": False
        })

    def get_tasks(self, username):
        return list(self.tasks.find({"username": username}))

    def complete_task(self, task_id):
        self.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"completed": True}}
        )

    def delete_task(self, task_id):
        self.tasks.delete_one({"_id": ObjectId(task_id)})

    def get_completion_percentage(self, tasks):
        if not tasks:
            return 0
        completed = sum(1 for t in tasks if t["completed"])
        return round((completed / len(tasks)) * 100)
