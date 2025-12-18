# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _name = "helpdesk_ticket"
    _inherit = [
        "helpdesk_ticket",
    ]

    odoo_implementation_id = fields.Many2one(
        string="# Odoo Implementation",
        comodel_name="odoo_implementation",
    )
    odoo_version_id = fields.Many2one(
        string="Odoo Version",
        comodel_name="odoo_version",
        related="odoo_implementation_id.version_id",
        store=True,
    )
    odoo_feature_ids = fields.Many2many(
        string="Related Odoo Features",
        comodel_name="odoo_feature",
        relation="helpdesk_ticket_odoo_feature_rel",
        column1="helpdesk_ticket_id",
        column2="odoo_feature_id",
    )
    odoo_use_case_ids = fields.Many2many(
        string="Related Odoo Use Cases",
        comodel_name="odoo_use_case",
        relation="helpdesk_ticket_odoo_use_case_rel",
        column1="helpdesk_ticket_id",
        column2="odoo_use_case_id",
    )

    # Change Request
    need_cr = fields.Boolean(
        string="Need Change Request",
    )
    odoo_change_request_ids = fields.Many2many(
        string="Odoo Change Requests",
        comodel_name="odoo_change_request",
        relation="helpdesk_ticket_odoo_change_request_rel",
        column1="helpdesk_ticket_id",
        column2="odoo_change_request_id",
    )
    cr_state = fields.Selection(
        string="CR State",
        selection=[
            ("not_needed", "Not Needed"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
        ],
        compute="_compute_cr_state",
        store=True,
        compute_sudo=True,
    )

    # CCR
    need_ccr = fields.Boolean(
        string="Need Customer Change Request",
    )
    odoo_configuration_change_record_ids = fields.Many2many(
        string="Odoo Configuration Change Records",
        comodel_name="odoo_configuration_change_record",
        relation="helpdesk_ticket_odoo_ccr_rel",
        column1="helpdesk_ticket_id",
        column2="odoo_ccr_id",
    )
    ccr_state = fields.Selection(
        string="CCR State",
        selection=[
            ("not_needed", "Not Needed"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
        ],
        compute="_compute_ccr_state",
        store=True,
        compute_sudo=True,
    )

    # Issue
    odoo_feature_issue_ids = fields.Many2many(
        string="Odoo Feature Issues",
        comodel_name="odoo_feature_issue",
        relation="helpdesk_ticket_odoo_feature_issue_rel",
        column1="helpdesk_ticket_id",
        column2="odoo_feature_issue_id",
    )
    issue_state = fields.Selection(
        string="Issue State",
        selection=[
            ("not_related", "Not Related"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
        ],
        compute="_compute_issue_state",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "odoo_feature_issue_ids.state",
        "odoo_feature_issue_ids",
    )
    def _compute_issue_state(self):
        for record in self.sudo():
            if not record.odoo_feature_issue_ids:
                record.issue_state = "not_related"
            elif (
                record.odoo_feature_issue_ids
                and record.odoo_feature_issue_ids.filtered(lambda r: r.state != "done")
            ):
                record.issue_state = "in_progress"
            else:
                record.issue_state = "done"

    @api.depends(
        "need_cr",
        "odoo_change_request_ids.state",
    )
    def _compute_cr_state(self):
        for record in self.sudo():
            if not record.need_cr:
                record.cr_state = "not_needed"
            elif record.need_cr and not record.odoo_change_request_ids:
                record.cr_state = "in_progress"
            elif (
                record.need_cr
                and record.odoo_change_request_ids
                and record.odoo_change_request_ids.filtered(lambda r: r.state != "done")
            ):
                record.cr_state = "in_progress"
            else:
                record.cr_state = "done"

    @api.depends(
        "need_ccr",
        "odoo_configuration_change_record_ids.state",
    )
    def _compute_ccr_state(self):
        for record in self.sudo():
            if not record.need_ccr:
                record.ccr_state = "not_needed"
            elif record.need_ccr and not record.odoo_configuration_change_record_ids:
                record.ccr_state = "in_progress"
            elif (
                record.need_ccr
                and record.odoo_configuration_change_record_ids
                and record.odoo_configuration_change_record_ids.filtered(
                    lambda r: r.state != "done"
                )
            ):
                record.ccr_state = "in_progress"
            else:
                record.ccr_state = "done"

    def onchange_odoo_implementation_id(self):
        self.odoo_implementation_id = False

    @api.onchange(
        "odoo_feature_id",
    )
    def onchange_odoo_feature_issue_id(self):
        self.odoo_feature_issue_id = False
