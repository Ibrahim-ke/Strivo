| Name           | Method | Endpoint                                                                              |
| -------------- | ------ | ------------------------------------------------------------------------------------- |
| Create Task    | POST   | `/api/method/strivo.api.task.api.create_task`                                             |
| Get My Tasks   | GET    | `/api/method/strivo.api.task.api.get_my_tasks`                                            |
| Get All Tasks  | GET    | `/api/method/strivo.api.task.api.get_all_tasks`                                           |
| Get A Task     | GET    | `/api/method/strivo.api.task.api.get_task?name=<task_id>`                                 |
| Update My Task | PUT    | `/api/method/strivo.api.task.api.update_task?name=<task_id>&priority=High&status=Blocked` |
| Add Dependency | PATCH  | `/api/method/strivo.api.task.api.add_dependency?task=TASK-0001&depends_on=TASK-0002`      |
| Add Comment    | PATCH  | `/api/method/strivo.api.task.api.add_comment?name=TASK-0001&comment_text=Almost done`     |
| Change Status  | PATCH  | `/api/method/strivo.api.task.api.change_status?name=TASK-0001&status=Completed`           |
| Delete Task    | DELETE | `/api/method/strivo.api.task.api.delete_task?name=TASK-0001`                              |
| Assign Task    | PATCH  | `/api/method/strivo.api.task.api.assign_task`                                             |
