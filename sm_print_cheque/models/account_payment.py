from odoo import _, api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    sm_amount_in_words = fields.Char(
        string="Cheque Amount in Words", compute="_compute_sm_amount_in_words")

    @api.depends("amount", "currency_id")
    def _compute_sm_amount_in_words(self):
        for payment in self:
            currency = payment.currency_id or payment.company_id.currency_id
            payment.sm_amount_in_words = currency.amount_to_text(payment.amount) if currency else ""

    def action_sm_print_cheque(self):
        self.ensure_one()
        return {
            "name": _("Print Cheque"),
            "type": "ir.actions.act_window",
            "res_model": "sm.print.cheque.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_payment_id": self.id,
                "default_move_id": (self.reconciled_invoice_ids | self.reconciled_bill_ids)[:1].id,
            },
        }
