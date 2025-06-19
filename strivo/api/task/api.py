import frappe
from frappe import _
from frappe.utils import nowdate

@frappe.whitelist()
def create_task(task_name, project, assigned_to, due_date=None, status="Open", priority="Medium", description=None):
    user = frappe.session.user
    roles = frappe.get_roles(user)

    # Only Project Manager can create tasks
    if "Project Manager" not in roles:
        frappe.throw(_("Only a Project Manager can create tasks."), frappe.PermissionError)

    doc = frappe.new_doc("Task")
    doc.task_name = task_name
    doc.project = project
    doc.assigned_to = assigned_to
    doc.status = status
    doc.priority = priority
    doc.due_date = due_date or nowdate()
    doc.description = description
    doc.insert(ignore_permissions=True)
    return {"message": "Task created", "task": doc.name}


@frappe.whitelist()
def get_my_tasks():
    user = frappe.session.user
    return frappe.get_all("Task", filters={"assigned_to": user}, fields=["name", "task_name", "status", "due_date", "priority"])


@frappe.whitelist()
def get_all_tasks(project=None):
    filters = {}
    if project:
        filters["project"] = project

    return frappe.get_all("Task", filters=filters, fields=["name", "task_name", "project", "status", "assigned_to", "priority", "due_date"])


@frappe.whitelist()
def get_task(name):
    try:
        return frappe.get_doc("Task", name).as_dict()
    except frappe.DoesNotExistError:
        frappe.throw(_("Task not found"), frappe.DoesNotExistError)


@frappe.whitelist()
def update_task(name, **kwargs):
    doc = frappe.get_doc("Task", name)

    for key, value in kwargs.items():
        if hasattr(doc, key):
            setattr(doc, key, value)

    doc.save(ignore_permissions=True)
    return {"message": "Task updated", "task": doc.name}


@frappe.whitelist()
def change_status(name, status):
    doc = frappe.get_doc("Task", name)
    doc.status = status
    doc.save(ignore_permissions=True)
    return {"message": "Task status updated", "status": status}


@frappe.whitelist()
def add_comment(name, comment_text):
    doc = frappe.get_doc("Task", name)
    doc.add_comment("Comment", comment_text)
    return {"message": "Comment added"}


@frappe.whitelist()
def add_dependency(task, depends_on):
    doc = frappe.get_doc("Task", task)
    doc.append("dependencies", {"depends_on": depends_on})
    doc.save(ignore_permissions=True)
    return {"message": "Dependency added"}


@frappe.whitelist()
def delete_task(name):
    user = frappe.session.user
    roles = frappe.get_roles(user)

    doc = frappe.get_doc("Task", name)

    # Only Project Managers or the task owner can delete
    if "Project Manager" not in roles and doc.assigned_to != user:
        frappe.throw(_("You are not allowed to delete this task"), frappe.PermissionError)

    frappe.delete_doc("Task", name, ignore_permissions=True)
    return {"message": "Task deleted"}
