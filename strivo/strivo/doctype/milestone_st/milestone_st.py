# Copyright (c) 2025, ibramiabdi.ke@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Milestone_st(Document):
  def before_save(self):
    if self.is_new() and not self.project_manager:
         self.manager = frappe.session.user
	
