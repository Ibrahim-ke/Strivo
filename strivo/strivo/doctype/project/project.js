// Copyright (c) 2025, ibramiabdi.ke@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project', {
  before_save(frm) {
    // Only set if it's a new document and the field is empty
    if (frm.is_new() && !frm.doc.project_manager) {
      frm.set_value('project_manager', frappe.session.user);
    }
  },

  refresh(frm) {
    frm.set_df_property('project_manager', 'read_only', 1);
  }
});
