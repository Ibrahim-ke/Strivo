import frappe
from frappe import _
from frappe.utils import nowdate

@frappe.whitelist(methods=["POST"])
def create_task():
    user = frappe.session.user
    roles = frappe.get_roles(user)

    # Only Project Manager can create tasks
    if "Project Manager" not in roles:
        frappe.throw(_("Only a Project Manager can create tasks."), frappe.PermissionError)

    data = frappe.request.get_json()

    if not data:
        frappe.throw(_("Missing request body."))

    title = data.get("title")
    project = data.get("project")
    due_date = data.get("due_date")
    status = data.get("status") or "Open"
    priority = data.get("priority") or "Medium"
    description = data.get("description")

    # Enforce mandatory fields
    if not title:
        frappe.throw(_("Task title (title) is required."))
    if not project:
        frappe.throw(_("Project is required."))

    # Ensure the project belongs to this project manager
    project_doc = frappe.get_doc("Project", project)
    if project_doc.project_manager != user:
        frappe.throw(_("You can only create tasks for projects you manage."), frappe.PermissionError)

    # Create the task
    doc = frappe.new_doc("Task")
    doc.title = title
    doc.project = project
    doc.assigned_to = user
    doc.start_date = nowdate()  # Automatically set
    doc.due_date = due_date or nowdate()
    doc.status = status
    doc.priority = priority
    doc.description = description
    doc.insert(ignore_permissions=True)

    return {
        "message": "Task created successfully.",
        "task": doc.name
    }


# @frappe.whitelist()
# def get_my_tasks():
#     user = frappe.session.user
#     return frappe.get_all("Task", filters={"assigned_to": user}, fields=["name", "title", "status", "project","start_date","end_date"])
@frappe.whitelist()
def get_my_tasks():
    user = frappe.session.user
    results = []

    # Get tasks assigned to current user
    tasks = frappe.get_all(
        "Task",
        filters={"assigned_to": user},
        fields=["name", "title", "status", "project", "start_date", "end_date"]
    )

    for task in tasks:
        try:
            project_doc = frappe.get_doc("Project", task.project)

            # Check if user is the Project Manager
            if project_doc.project_manager == user:
                authorized = True
            else:
                # Check if user is in team_members
                authorized = any(member.team_member == user for member in project_doc.get("team_members", []))

            if not authorized:
                continue

            # Get full task document
            doc = frappe.get_doc("Task", task.name)
            task_dict = {
                "name": doc.name,
                "title": doc.title,
                "status": doc.status,
                "project": doc.project,
                "start_date": doc.start_date,
                "end_date": doc.end_date,
                "dependencies": [
                    {
                        "depends_on": d.depends_on,
                        "dependency_type": d.dependacy_type
                    } for d in (doc.get("dependecy") or [])
                ],
                "comments": [
                    {
                        "commentor": c.commentor,
                        "comment": c.comment
                    } for c in (doc.get("comments") or [])
                ]
            }
            results.append(task_dict)

        except frappe.DoesNotExistError:
            continue

    return results



@frappe.whitelist()
def get_all_tasks(project=None):
    user = frappe.session.user
    authorized_projects = set()

    # Optional project filter
    project_filters = {"name": project} if project else {}
    all_projects = frappe.get_all("Project", filters=project_filters, fields=["name", "project_manager"])

    for proj in all_projects:
        if proj.project_manager == user:
            authorized_projects.add(proj.name)
            continue

        project_doc = frappe.get_doc("Project", proj.name)
        for member in project_doc.get("team_members", []):
            if member.team_member == user:
                authorized_projects.add(proj.name)
                break

    # Get all tasks directly assigned to the user
    assigned_tasks = frappe.get_all(
        "Task",
        filters={"assigned_to": user},
        fields=["name", "project"]
    )
    assigned_projects = {task.project for task in assigned_tasks}

    # Merge project access from assignment and team roles
    all_authorized_projects = list(authorized_projects.union(assigned_projects))

    if not all_authorized_projects:
        return []

    # Fetch tasks from all authorized projects
    tasks = frappe.get_all(
        "Task",
        filters={"project": ["in", all_authorized_projects]},
        fields=["name", "title", "description", "project", "status", "assigned_to", "start_date","end_date"]
    )

    enriched_tasks = []
    for task in tasks:
        doc = frappe.get_doc("Task", task.name)

        enriched_tasks.append({
            "name": doc.name,
            "title": doc.title,
            "description": doc.description,
            "project": doc.project,
            "status": doc.status,
            "assigned_to": doc.assigned_to,
           "start_date": doc.start_date,
            "end_date": doc.end_date,
            "dependencies": [
                {
                    "depends_on": d.depends_on,
                    "dependency_type": d.dependacy_type
                } for d in (doc.get("dependecy") or [])
            ],
            "comments": [
                {
                    "commentor": c.commentor,
                    "comment": c.comment
                } for c in (doc.get("comments") or [])
            ]
        })

    return enriched_tasks



@frappe.whitelist()
def get_task(name):
    user = frappe.session.user

    try:
        task = frappe.get_doc("Task", name)
        project = frappe.get_doc("Project", task.project)

        # Case 1: User is the assigned user
        if task.assigned_to == user:
            return task.as_dict()

        # Case 2: User is the project manager
        if project.project_manager == user:
            return task.as_dict()

        # Case 3: User is a project team member
        for member in project.get("team_members", []):
            if member.team_member == user:
                return task.as_dict()

        # Unauthorized
        frappe.throw(_("You are not authorized to view this task."), frappe.PermissionError)

    except frappe.DoesNotExistError:
        frappe.throw(_("Task not found"), frappe.DoesNotExistError)



@frappe.whitelist(methods=["PATCH"])
def update_task(name):
    user = frappe.session.user
    allowed_fields = ["title", "start_date", "end_date", "status", "description"]

    doc = frappe.get_doc("Task", name)

    # Only the assigned user can update
    if doc.assigned_to != user:
        frappe.throw(_("Only the assigned user can update this task."), frappe.PermissionError)

    data = frappe.request.get_json()
    if not data:
        frappe.throw(_("No input data found."))

    updated = False
    for key in allowed_fields:
        if key in data:
            setattr(doc, key, data[key])
            updated = True

    if not updated:
        frappe.throw(_("No valid fields to update."))

    doc.save(ignore_permissions=True)
    return {
        "message": "Task updated successfully",
        "task": doc.name
    }



@frappe.whitelist(methods=["PATCH"])
def change_status(name, status):
    user = frappe.session.user

    # Fetch the task
    doc = frappe.get_doc("Task", name)

    # Fetch the related project
    project = frappe.get_doc("Project", doc.project)

    # Allow only if user is the assigned_to or project manager
    if doc.assigned_to != user and project.project_manager != user:
        frappe.throw(_("You are not authorized to update the status of this task."), frappe.PermissionError)

    # Update the status
    doc.status = status
    doc.save(ignore_permissions=True)

    return {
        "message": "Task status updated",
        "status": doc.status
    }



@frappe.whitelist(methods=["PATCH"])
def add_comment(name):
    user = frappe.session.user
    data = frappe.request.get_json()

    if not data or not data.get("comment"):
        frappe.throw(_("Comment text is required."))

    # Fetch task and project
    task = frappe.get_doc("Task", name)
    project = frappe.get_doc("Project", task.project)

    # Check if user is allowed (Project Manager or team member)
    authorized = (
        project.project_manager == user or
        any(member.team_member == user for member in project.get("team_members", []))
    )

    if not authorized:
        frappe.throw(_("You are not authorized to comment on this task."), frappe.PermissionError)

    # Append to child table (assuming child table is `comments` and doctype is `Task_Comment`)
    task.append("comments", {
        "commentor": user,
        "comment": data.get("comment")
    })

    task.save(ignore_permissions=True)

    return {"message": "Comment added successfully"}




@frappe.whitelist(methods=["PATCH"])
def add_dependency(name):
    user = frappe.session.user
    data = frappe.request.get_json()

    if not data or not data.get("depends_on"):
        frappe.throw(_("Field 'depends_on' is required."))

    # Fetch the Task
    doc = frappe.get_doc("Task", name)
    project = frappe.get_doc("Project", doc.project)

    # Check if user is the project manager or the task assignee
    if project.project_manager != user and doc.assigned_to != user:
        frappe.throw(_("Only the Project Manager or the assignee can add dependencies."), frappe.PermissionError)

    # Append to dependency child table (assuming 'dependencies' is the field name)
    doc.append("dependecy", {
        "depends_on": data.get("depends_on"),
        "dependacy_type": data.get("dependacy_type") or "Blocking"  # Optional: default to "Blocking"
    })

    doc.save(ignore_permissions=True)

    return {"message": "Dependency added successfully"}


@frappe.whitelist()
def delete_task(name):
    user = frappe.session.user

    doc = frappe.get_doc("Task", name)

    # Only the assigned user can delete the task
    if doc.assigned_to != user:
        frappe.throw(_("You are not allowed to delete this task"), frappe.PermissionError)

    frappe.delete_doc("Task", name, ignore_permissions=True)
    return {"message": "Task deleted"}

@frappe.whitelist(methods=["PATCH"])
def assign_task(name):
    user = frappe.session.user
    roles = frappe.get_roles(user)

    # Check permission
    if "Project Manager" not in roles:
        frappe.throw(_("Only a Project Manager can assign tasks."), frappe.PermissionError)

    data = frappe.request.get_json()
    if not data or not data.get("assigned_to"):
        frappe.throw(_("assigned_to is required in the request body."))

    assigned_to = data.get("assigned_to")

    # Get the task
    doc = frappe.get_doc("Task", name)

    # Update assigned_to
    doc.assigned_to = assigned_to
    doc.save(ignore_permissions=True)

    return {
        "message": "Task assigned successfully",
        "task": doc.name,
        "assigned_to": doc.assigned_to
    }


