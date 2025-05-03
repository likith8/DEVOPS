from bson import ObjectId
from datetime import datetime
import pytz
from bson.codec_options import CodecOptions

# Timezone for Asia/Kolkata
IST = pytz.timezone("Asia/Kolkata")

class TaskModel:
    def __init__(self, mongo):
        self.tasks = mongo.db.tasks.with_options(
            codec_options=CodecOptions(tz_aware=True, tzinfo=IST)
        )

    def _localize_datetime(self, dt):
        if dt.tzinfo is None:
            return IST.localize(dt)
        return dt.astimezone(IST)

    def add_task(self, username, task_text, end_time=None, priority="Medium", category="Others",
                 tags=None, recurrence="none", subtasks=None):
        start_time = self._localize_datetime(datetime.now())

        if end_time:
            end_time = self._localize_datetime(end_time)

        task_data = {
            "username": username,
            "task": task_text,
            "completed": False,
            "start_time": start_time,
            "end_time": end_time,
            "priority": priority,
            "category": category,
            "tags": tags or [],
            "recurrence": recurrence,
            "subtasks": []
        }

        if subtasks:
            task_data["subtasks"] = [{
                "_id": ObjectId(),
                "text": text.strip(),
                "completed": False
            } for text in subtasks if text.strip()]  # Ensure no empty subtasks

        self.tasks.insert_one(task_data)

    def get_tasks(self, username, category=None, sort_by="priority"):
        query = {"username": username}
        if category:
            query["category"] = category

        tasks = list(self.tasks.find(query))
        priority_order = {"High": 1, "Medium": 2, "Low": 3}

        if sort_by == "priority":
            tasks.sort(key=lambda t: priority_order.get(t.get("priority", "Medium")))

        for task in tasks:
            task['start_time_str'] = task['start_time'].strftime('%Y-%m-%d %H:%M:%S') if task.get('start_time') else None
            task['end_time_str'] = task['end_time'].strftime('%Y-%m-%d %H:%M:%S') if task.get('end_time') else None

        return tasks

    def complete_task(self, task_id):
        completion_time = self._localize_datetime(datetime.now())
        task = self.tasks.find_one({"_id": ObjectId(task_id)})
        update_data = {
            "completed": True,
            "completion_date": completion_time
        }
        if not task.get("end_time"):
            update_data["end_time"] = completion_time
        self.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_data}
        )

    def delete_task(self, task_id):
        self.tasks.delete_one({"_id": ObjectId(task_id)})

    def get_completion_percentage(self, tasks):
        if not tasks:
            return 0
        completed_count = sum(1 for task in tasks if task.get("completed"))
        return round((completed_count / len(tasks)) * 100)

    def add_subtask(self, task_id, subtask_text):
        subtask = {
            "_id": ObjectId(),
            "text": subtask_text.strip(),
            "completed": False
        }
        self.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$push": {"subtasks": subtask}}
        )

    def complete_subtask(self, subtask_id):
        result = self.tasks.update_one(
            {"subtasks._id": ObjectId(subtask_id)},
            {"$set": {"subtasks.$.completed": True}}
        )
        if result.matched_count == 0:
            raise ValueError(f"Subtask with ID {subtask_id} not found")

    def get_subtask_progress(self, task_id):
        task = self.tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        total_subtasks = len(task.get("subtasks", []))
        if total_subtasks == 0:
            return 100

        completed_subtasks = sum(1 for subtask in task["subtasks"] if subtask["completed"])
        return round((completed_subtasks / total_subtasks) * 100)

    def get_upcoming_tasks(self, current_time):
        current_time = self._localize_datetime(current_time)
        return list(self.tasks.find({
            "end_time": {"$gte": current_time},
            "completed": False
        }))

    def add_recurring_task(self, username, task_text, end_time=None, priority="Medium", category="Others",
                           recurrence="daily"):
        start_time = self._localize_datetime(datetime.now())

        if end_time:
            end_time = self._localize_datetime(end_time)

        # Add logic for recurrence handling (not implemented here)
        self.tasks.insert_one({
            "username": username,
            "task": task_text,
            "completed": False,
            "start_time": start_time,
            "end_time": end_time,
            "priority": priority,
            "category": category,
            "recurrence": recurrence,
            "subtasks": []
        })

    def get_tasks_by_tags(self, username, tags):
        query = {"username": username, "tags": {"$in": tags}}
        return list(self.tasks.find(query))

    def search_tasks(self, username, keyword):
        query = {"username": username, "$text": {"$search": keyword}}
        return list(self.tasks.find(query))

    def get_tasks_by_category(self, username, category):
        query = {"username": username, "category": category}
        return list(self.tasks.find(query))

    def delete_subtask(self, subtask_id):
        self.tasks.update_one(
            {"subtasks._id": ObjectId(subtask_id)},
            {"$pull": {"subtasks": {"_id": ObjectId(subtask_id)}}}
        )
