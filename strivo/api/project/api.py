import frappe
from frappe import _
from frappe.model.document import Document

@frappe.whitelist(methods=["POST"])
def create_project():
    user = frappe.session.user
    roles = frappe.get_roles(user)

    # Only Project Manager can create a project
    if "Project Manager" not in roles:
        frappe.throw(_("You are not authorized to create a project."), frappe.PermissionError)

    data = frappe.request.get_json()

    required_fields = ["project_name", "start_date", "end_date"]
    for field in required_fields:
        if not data.get(field):
            frappe.throw(_(f"{field.replace('_', ' ').title()} is required."), frappe.MandatoryError)

    doc = frappe.new_doc("Project")
    doc.project_name = data.get("project_name")
    doc.start_date = data.get("start_date")
    doc.end_date = data.get("end_date")
    doc.project_manager = user  # Set automatically

    # Optional fields
    optional_fields = [
        "priority",
        "status",
        "tags",
        "project_type",
        "description",
        "team_members"  # expects list of dicts
    ]

    for field in optional_fields:
        if field in data:
            doc.set(field, data.get(field))

    doc.insert()

    return {
        "message": "Project created successfully",
        "project": doc.name,
        "project_name": doc.project_name
    }



@frappe.whitelist(methods=["GET"])
def get_all_projects():
    user = frappe.session.user
    roles = frappe.get_roles(user)

    # Fetch all projects (minimum fields for performance)
    all_projects = frappe.get_all("Project", fields=["name", "project_name", "status", "end_date", "priority", "project_manager"])

    result = []

    for project in all_projects:
        # Case 1: Project Manager is the current user
        if project.project_manager == user:
            result.append(project)
            continue

        # Case 2: Team member in child table
        doc = frappe.get_doc("Project", project.name)

        for member in doc.get("team_members", []):
            if member.team_member == user:
                result.append(project)
                break

    return result

    
@frappe.whitelist(methods=["GET"])
def get_project(name):
    user = frappe.session.user

    # Try to load the project
    try:
        doc = frappe.get_doc("Project", name)
    except frappe.DoesNotExistError:
        frappe.throw(_("Project not found"), frappe.DoesNotExistError)

    # Permission check
    is_project_manager = doc.project_manager == user
    is_team_member = any(row.team_member == user for row in doc.get("team_members", []) if row.team_member)

    if not (is_project_manager or is_team_member):
        frappe.throw(_("You are not authorized to view this project."), frappe.PermissionError)

    # Return only relevant fields
    return {
        "name": doc.name,
        "project_name": doc.project_name,
        "project_manager": doc.project_manager,
        "status": doc.status,
        "priority": doc.priority,
        "project_type": doc.project_type,
        "start_date": doc.start_date,
        "end_date": doc.end_date,
        "tags": doc.tags,
        "description": doc.description,
        "team_members": [
            {
                "team_member": row.team_member,
                "is_team_lead": row.is_team_lead
            }
            for row in doc.get("team_members", []) if row.team_member
        ]
    }




@frappe.whitelist(methods=["DELETE"])
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

@frappe.whitelist(methods=["PATCH"])
def change_status(name, status):
    allowed_statuses = ["Planned", "In progress", "On Hold", "Completed"]
    user = frappe.session.user
    doc = frappe.get_doc("Project", name)

    # Check if user is the assigned project manager
    if doc.project_manager != user:
        frappe.throw(_("Only the assigned Project Manager can update the status."), frappe.PermissionError)

    # Validate the status
    if status not in allowed_statuses:
        frappe.throw(_("Invalid status. Must be one of: {0}").format(", ".join(allowed_statuses)), frappe.ValidationError)

    # Update status
    doc.status = status
    doc.save(ignore_permissions=True)

    return {
        "message": "Status updated successfully.",
        "project": doc.name,
        "new_status": doc.status
    }

@frappe.whitelist(methods=["PATCH"])
def change_project_type(name, project_type):
    allowed_types = ["Internal", "Client", "Research"]
    user = frappe.session.user

    # Fetch project document
    doc = frappe.get_doc("Project", name)

    # Check if current user is the assigned project manager
    if doc.project_manager != user:
        frappe.throw(_("Only the assigned Project Manager can update the project type."), frappe.PermissionError)

    # Validate project type
    if project_type not in allowed_types:
        frappe.throw(_("Invalid project type. Must be one of: {0}").format(", ".join(allowed_types)), frappe.ValidationError)

    # Update project type
    doc.project_type = project_type
    doc.save(ignore_permissions=True)

    return {
        "message": "Project type updated successfully.",
        "project": doc.name,
        "new_project_type": doc.project_type
    }

@frappe.whitelist(methods=["PATCH"])
def change_priority(name, priority):
    allowed_priorities = ["Low", "Medium", "High", "Critical"]
    user = frappe.session.user

    # Fetch project
    doc = frappe.get_doc("Project", name)

    # Permission check
    if doc.project_manager != user:
        frappe.throw(_("Only the assigned Project Manager can update the priority."), frappe.PermissionError)

    # Validate priority
    if priority not in allowed_priorities:
        frappe.throw(_("Invalid priority. Must be one of: {0}").format(", ".join(allowed_priorities)), frappe.ValidationError)

    # Update and save
    doc.priority = priority
    doc.save(ignore_permissions=True)

    return {
        "message": "Priority updated successfully.",
        "project": doc.name,
        "new_priority": doc.priority
    }


@frappe.whitelist(methods=["PUT"])
def update_project():
    data = frappe.request.get_json()

    if not data or "name" not in data:
        frappe.throw(_("Project name (`name`) is required."), frappe.MandatoryError)

    name = data.get("name")

    try:
        doc = frappe.get_doc("Project", name)
    except frappe.DoesNotExistError:
        frappe.throw(_("Project not found."), frappe.DoesNotExistError)

    # Check permission: only project manager can update
    if doc.project_manager != frappe.session.user:
        frappe.throw(_("You are not authorized to update this project."), frappe.PermissionError)

    # Allowed fields to update
    allowed_fields = [
        "project_name", "start_date", "end_date", "status", "priority",
        "tags", "project_type", "description"
    ]

    # Update fields dynamically (like JS spread)
    for field in allowed_fields:
        if field in data:
            doc.set(field, data[field])

    doc.save()

    return {
        "message": "Project updated successfully",
        "project": doc.name,
        "updated_fields": {k: v for k, v in data.items() if k in allowed_fields}
    }



@frappe.whitelist(methods=["PATCH"])
def add_tags(name, tags):
    doc = frappe.get_doc("Project", name)
    doc.tags = tags  # make sure you added a "tags" field of type Data or Small Text
    doc.save(ignore_permissions=True)
    return {"message": "Tags updated", "tags": doc.tags}


# @frappe.whitelist()
# def get_all_projects():
#     user = frappe.session.user
#     roles = frappe.get_roles(user)
#     project_doc=frappe.get_all("")
#     # project_doc = frappe.get_doc("Project", project)
#     if "Project Manager" in roles:
#         if project_doc.project_manager != user:
#           frappe.throw(_("You can only view  milestones  projects."), frappe.PermissionError)

#         return frappe.get_all(
#             "Project",
#             fields=["name", "project_name", "status", "end_date", "priority"]
#         )

#     # For team members, filter by user in project_team child table
#     all_projects = frappe.get_all("Project", fields=["name", "project_name", "status", "end_date", "priority"])
#     filtered = []

#     for project in all_projects:
#         try:
#             doc = frappe.get_doc("Project", project.name)
#             # Avoid permission errors
#             doc.check_permission()  # Optional strict check
#         except frappe.PermissionError:
#             doc = frappe.get_doc("Project", project.name)
#             doc = doc.load_from_db()  # bypass permission check
#             frappe.local.flags.ignore_permissions = True

#         for row in doc.get("team_members", []):
#             if row.team_member == user:
#                 filtered.append(project)
#                 break

#     return filtered