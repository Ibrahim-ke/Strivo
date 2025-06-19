import frappe

@frappe.whitelist(allow_guest=True)
def ping():
     return 'pong'
# /api/method/strivo.api.api.ping