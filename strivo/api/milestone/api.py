import frappe
from frappe import _

@frappe.whitelist(methods=["POST"])
def create_milestone():
    user = frappe.session.user
    roles = frappe.get_roles(user)
    data = frappe.local.form_dict

    title = data.get("title")
    project = data.get("project")
    due_date = data.get("due_date")
    status = data.get("status", "Not Started")
    description = data.get("description")

    # Validate required fields
    if not title or not project or not due_date:
        frappe.throw(_("Fields 'title', 'project', and 'due_date' are mandatory."), frappe.MandatoryError)

    # Ensure only Project Managers can create
    if "Project Manager" not in roles:
        frappe.throw(_("Only a Project Manager can create milestones."), frappe.PermissionError)

    # Check project ownership
    try:
        project_doc = frappe.get_doc("Project", project)
        if project_doc.project_manager != user:
            frappe.throw(_("You can only create milestones for projects you manage."), frappe.PermissionError)
    except frappe.DoesNotExistError:
        frappe.throw(_("Project not found."), frappe.DoesNotExistError)

    # Create milestone
    doc = frappe.new_doc("Milestone_st")
    doc.title = title
    doc.project = project
    doc.status = status
    doc.description = description
    doc.due_date = due_date
    doc.owner = user
    doc.insert(ignore_permissions=True)

    return {
        "message": "Milestone created",
        "milestone": doc.name
    }



@frappe.whitelist(methods=["GET"])
def get_all_milestones():
    user = frappe.session.user
    authorized_projects = []

    all_projects = frappe.get_all("Project", fields=["name", "project_manager"])

    for project in all_projects:
        # Check if user is the project manager
        if project.project_manager == user:
            authorized_projects.append(project.name)
            continue

        # Otherwise check if user is in project team
        doc = frappe.get_doc("Project", project.name)
        for member in doc.get("team_members", []):
            if member.team_member == user:
                authorized_projects.append(project.name)
                break

    if not authorized_projects:
        return []

    milestones = frappe.get_all(
        "Milestone_st",
        filters={"project": ["in", authorized_projects]},
        fields=["name", "title", "status", "project","due_date", "description"]
    )

    return milestones




@frappe.whitelist(methods=["GET"])
def get_milestone(name):
    try:
        user = frappe.session.user
        milestone = frappe.get_doc("Milestone_st", name)
        project = frappe.get_doc("Project", milestone.project)

        # Authorization check
        if project.project_manager == user or any(member.team_member == user for member in project.get("team_members", [])):
            return {
                "name": milestone.name,
                "title": milestone.title,
                "status": milestone.status,
                "project": milestone.project,
                "project_manager": project.project_manager,
                "due_date": milestone.due_date,
                "description": milestone.description,
            }

        frappe.throw(_("You are not authorized to view this milestone."), frappe.PermissionError)

    except frappe.DoesNotExistError:
        frappe.throw(_("Milestone not found."), frappe.DoesNotExistError)


@frappe.whitelist(methods=["PUT"])
def update_milestone(name):
    user = frappe.session.user
    roles = frappe.get_roles(user)

    # Parse JSON body
    data = frappe.local.form_dict
    if isinstance(data, str):
        data = frappe.json.loads(data)

    milestone_name = data.get("title")
    status = data.get("status")
    description = data.get("description")

    # Fetch doc
    doc = frappe.get_doc("Milestone_st", name)

    # Permission check: Only owner or Project Manager
    if doc.owner != user and "Project Manager" not in roles:
        frappe.throw("You are not authorized to update this milestone.", frappe.PermissionError)

    # Identity check (e.g., compare current and provided name)
    if milestone_name and doc.milestone_name != milestone_name:
        frappe.throw("Milestone name does not match existing record.", frappe.ValidationError)

    # Update allowed fields
    if status:
        doc.status = status
    if description:
        doc.description = description

    doc.save(ignore_permissions=True)

    return {
        "message": "Milestone updated",
        "milestone": doc.name
    }


@frappe.whitelist(methods=["DELETE"])
def delete_milestone(name):
    user = frappe.session.user
    roles = frappe.get_roles(user)

    # Ensure the user is a Project Manager
    if "Project Manager" not in roles:
        frappe.throw(_("Only a Project Manager can delete milestones."), frappe.PermissionError)

    # Get the milestone
    doc = frappe.get_doc("Milestone_st", name)

    # Ensure the user is the one who created the milestone
    if doc.owner != user:
        frappe.throw(_("You can only delete milestones you created."), frappe.PermissionError)

    # Ensure the user is the project manager for the associated project
    project_doc = frappe.get_doc("Project", doc.project)
    if project_doc.project_manager != user:
        frappe.throw(_("You can only delete milestones for your own projects."), frappe.PermissionError)

    # Delete the milestone
    frappe.delete_doc("Milestone_st", name, ignore_permissions=True)
    return {"message": "Milestone deleted"}



@frappe.whitelist(methods=["PATCH"])
def change_status(name):
    allowed_statuses = ["Planned", "Achieved", "Missed"]
    user = frappe.session.user

    data = frappe.request.get_json()
    if not data or not data.get("status"):
        frappe.throw(_("Status is required in request body."))

    status = data.get("status")

    try:
        doc = frappe.get_doc("Milestone_st", name)
    except frappe.DoesNotExistError:
        frappe.throw(_("Milestone not found."), frappe.DoesNotExistError)

    if doc.owner != user:
        frappe.throw(_("You are not authorized to update the status of this milestone."), frappe.PermissionError)

    if status not in allowed_statuses:
        frappe.throw(_("Invalid status. Allowed statuses are: {0}").format(", ".join(allowed_statuses)))

    doc.status = status
    doc.save(ignore_permissions=True)

    return {
        "message": "Status updated",
        "status": doc.status
    }


# @frappe.whitelist()
# def change_description(name, description):
#     doc = frappe.get_doc("Milestone", name)
#     doc.description = description
#     doc.save(ignore_permissions=True)
#     return {"message": "Description updated"}


# @frappe.whitelist(methods=["GET"])
# def get_milestone(name):
#     try:
#         user = frappe.session.user
#         milestone = frappe.get_doc("Milestone_st", name)
#         project = frappe.get_doc("Project", milestone.project)

#         # Allow if user is project manager
#         if project.project_manager == user:
#             return milestone.as_dict()

#         # Check if user is in project team
#         for member in project.get("team_members", []):
#             if member.team_member == user:
#                 return milestone.as_dict()

#         # If user is not authorized
#         frappe.throw(_("You are not authorized to view this milestone."), frappe.PermissionError)

#     except frappe.DoesNotExistError:
#         frappe.throw(_("Milestone not found."), frappe.DoesNotExistError)
