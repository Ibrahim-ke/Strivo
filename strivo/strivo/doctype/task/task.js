frappe.ui.form.on('Task', {
  refresh(frm) {
    const status = frm.doc.status;
   console.log("Status is:", frm.doc.status);
    if (status === "In_progress") {
      frm.page.set_indicator(__('In Progress'), 'yellow');
    } else if (status === "Done") {
      frm.page.set_indicator(__('Done'), 'green');
    } else if (status === "Blocked") {
      frm.page.set_indicator(__('Blocked'), 'red');
    }
  }
});
