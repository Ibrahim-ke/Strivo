import frappe
from frappe import _
from frappe.model.document import Document

@frappe.whitelist()
def create_project(project_name, end_date=None):
    user = frappe.session.user
    doc = frappe.new_doc("Project")
    doc.project_name = project_name
    doc.project_manager = user
    if end_date:
        doc.end_date = end_date
    doc.insert(ignore_permissions=True)
    return {
        "message": "Project created successfully",
        "project": doc.name,
        "project_name": doc.project_name
    }

@frappe.whitelist()
def get_all_projects():
    user = frappe.session.user
    roles = frappe.get_roles(user)

    if "Project Manager" in roles:
        return frappe.get_all(
            "Project",
            fields=["name", "project_name", "status", "end_date", "priority"]
        )

    # For team members, filter by user in project_team child table
    all_projects = frappe.get_all("Project", fields=["name", "project_name", "status", "end_date", "priority"])
    filtered = []

    for project in all_projects:
        try:
            doc = frappe.get_doc("Project", project.name)
            # Avoid permission errors
            doc.check_permission()  # Optional strict check
        except frappe.PermissionError:
            doc = frappe.get_doc("Project", project.name)
            doc = doc.load_from_db()  # bypass permission check
            frappe.local.flags.ignore_permissions = True

        for row in doc.get("team_members", []):
            if row.team_member == user:
                filtered.append(project)
                break

    return filtered

    

@frappe.whitelist()
def get_project(name):
    return frappe.get_doc("Project", name).as_dict()


@frappe.whitelist()
def delete_project(name):
    user = frappe.session.user
    roles = frappe.get_roles(user)

    # Check if user has Project Manager role
    if "Project Manager" not in roles:
        frappe.throw(_("You are not authorized to delete projects."), frappe.PermissionError)

    # Try fetching the project
    try:
        doc = frappe.get_doc("Project", name)
    except frappe.DoesNotExistError:
        frappe.throw(_("Project does not exist."), frappe.DoesNotExistError)

    # Check if the current user is the project manager
    if doc.project_manager != user:
        frappe.throw(_("Only the project manager who created this project can delete it."), frappe.PermissionError)

    # All checks passed, delete the project
    frappe.delete_doc("Project", name, ignore_permissions=True)
    return {"message": "Project deleted successfully"}

@frappe.whitelist()
def change_status(name, status):
    doc = frappe.get_doc("Project", name)
    doc.status = status
    doc.save(ignore_permissions=True)
    return {"message": "Status updated", "status": doc.status}

@frappe.whitelist()
def update_project(name, project_name=None, end_date=None):
    doc = frappe.get_doc("Project", name)
    if project_name:
        doc.project_name = project_name
    if end_date:
        doc.end_date = end_date
    doc.save(ignore_permissions=True)
    return {"message": "Project updated", "project": doc.name}

@frappe.whitelist()
def add_tags(name, tags):
    doc = frappe.get_doc("Project", name)
    doc.tags = tags  # make sure you added a "tags" field of type Data or Small Text
    doc.save(ignore_permissions=True)
    return {"message": "Tags updated", "tags": doc.tags}
