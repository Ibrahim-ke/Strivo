import frappe
from frappe import _

@frappe.whitelist()
def create_milestone(title, project, status=None, description=None):
    user = frappe.session.user
    roles = frappe.get_roles(user)

    # Ensure only Project Managers can create
    if "Project Manager" not in roles:
        frappe.throw(_("Only a Project Manager can create milestones."), frappe.PermissionError)

    # Ensure the project belongs to this Project Manager
    project_doc = frappe.get_doc("Project", project)
    if project_doc.project_manager != user:
        frappe.throw(_("You can only create milestones for projects you manage."), frappe.PermissionError)

    doc = frappe.new_doc("Milestone_st")
    doc.title = title
    doc.project = project
    doc.status = status or "Not Started"
    doc.description = description
    doc.owner = user
    doc.insert(ignore_permissions=True)

    return {"message": "Milestone created", "milestone": doc.name}


@frappe.whitelist()
def get_all_milestones(project=None):
    filters = {}
    if project:
        filters["project"] = project

    return frappe.get_all("Milestone", filters=filters, fields=["name", "milestone_name", "status", "project", "description"])


@frappe.whitelist()
def get_milestone(name):
    try:
        return frappe.get_doc("Milestone", name).as_dict()
    except frappe.DoesNotExistError:
        frappe.throw(_("Milestone not found"), frappe.DoesNotExistError)


@frappe.whitelist()
def update_milestone(name, milestone_name=None, status=None, description=None):
    doc = frappe.get_doc("Milestone", name)

    if milestone_name:
        doc.milestone_name = milestone_name
    if status:
        doc.status = status
    if description:
        doc.description = description

    doc.save(ignore_permissions=True)
    return {"message": "Milestone updated", "milestone": doc.name}


@frappe.whitelist()
def delete_milestone(name):
    user = frappe.session.user
    roles = frappe.get_roles(user)

    if "Project Manager" not in roles:
        frappe.throw(_("Only a Project Manager can delete milestones."), frappe.PermissionError)

    doc = frappe.get_doc("Milestone", name)
    project_doc = frappe.get_doc("Project", doc.project)

    if project_doc.project_manager != user:
        frappe.throw(_("You can only delete milestones for your own projects."), frappe.PermissionError)

    frappe.delete_doc("Milestone", name, ignore_permissions=True)
    return {"message": "Milestone deleted"}


@frappe.whitelist()
def change_status(name, status):
    doc = frappe.get_doc("Milestone", name)
    doc.status = status
    doc.save(ignore_permissions=True)
    return {"message": "Status updated", "status": status}


@frappe.whitelist()
def change_description(name, description):
    doc = frappe.get_doc("Milestone", name)
    doc.description = description
    doc.save(ignore_permissions=True)
    return {"message": "Description updated"}
