# /api/method/strivo.api.project.create_project
| Endpoint Name    | Method | Path                                              |
| ---------------- | ------ | ------------------------------------------------- |
| Create Project   | POST   | `/api/method/strivo.api.project.api.create_project`   |
| Get All Projects | GET    | `/api/method/strivo.api.project.api.get_all_projects` |
| Get One Project  | GET    | `/api/method/strivo.api.project.api.get_project`      |
| Delete Project   | DELETE | `/api/method/strivo.api.project.api.delete_project`   |
| Change Status    | PATCH  | `/api/method/strivo.api.project.api.change_status`    |
| Update Project   | PUT    | `/api/method/strivo.api.project.api.update_project`   |
| Add Tags         | PATCH  | `/api/method/strivo.api.project.api.add_tags`         |
| Change Project Type         | PATCH  | `/api/method/strivo.api.project.api.change_project_type`         |



# Sample body
## Create project
```json 
{
  "project_name": "Research Portal",
  "start_date": "2025-06-20",
  "end_date": "2025-07-20",
  "priority": "High",
  "status": "Planned",
  "tags": "urgent,client",
  "project_type": "Client",
  "description": "Build a platform for research data.",
  "team_members": [
    {
      "team_member": "member1@strivo.com",
      "is_team_lead": 1
    }
  ]
}
```
