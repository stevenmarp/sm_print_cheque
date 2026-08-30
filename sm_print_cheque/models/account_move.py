from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _sm_print_cheque_payments(self):
        self.ensure_one()
        Payment = self.env["account.payment"]
        payments = Payment.search([("invoice_ids", "in", self.ids)])
        payments |= Payment.search([("reconciled_invoice_ids", "in", self.ids)])
        payments |= Payment.search([("reconciled_bill_ids", "in", self.ids)])
        return payments.sorted(lambda p: (p.date, p.id), reverse=True)

    def action_sm_print_cheque(self):
        self.ensure_one()
        if self.state != "posted":
            raise UserError(_("Only posted invoices or bills can be printed as cheques."))
        payments = self._sm_print_cheque_payments()
        if not payments:
            raise UserError(_("No payment is linked to this document. Register a payment first."))
        return {
            "name": _("Print Cheque"),
            "type": "ir.actions.act_window",
            "res_model": "sm.print.cheque.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_move_id": self.id,
                "default_payment_id": payments[:1].id,
            },
        }
