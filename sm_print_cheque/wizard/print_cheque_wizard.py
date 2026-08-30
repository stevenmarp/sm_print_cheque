from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SmPrintChequeWizard(models.TransientModel):
    _name = "sm.print.cheque.wizard"
    _description = "Print Cheque"

    payment_id = fields.Many2one("account.payment", required=True)
    move_id = fields.Many2one("account.move", string="Document")
    cheque_format_id = fields.Many2one("sm.cheque.format", string="Cheque Format", required=True)
    free_text = fields.Char()
    free_text_two = fields.Char()
    partner_title = fields.Char()
    cheque_no = fields.Char()

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        company = self.env.company
        cheque_format = self.env["sm.cheque.format"].search([
            ("company_id", "=", company.id),
            ("default_template", "=", True),
        ], limit=1)
        if not cheque_format:
            cheque_format = self.env["sm.cheque.format"].search([("company_id", "=", company.id)], limit=1)
        if cheque_format:
            values.setdefault("cheque_format_id", cheque_format.id)
        payment = self.env["account.payment"].browse(values.get("payment_id"))
        if payment:
            values.setdefault("partner_title", "")
            values.setdefault("cheque_no", payment.payment_reference or payment.name or "")
        return values

    @api.onchange("move_id")
    def _onchange_move_id(self):
        if self.move_id and not self.payment_id:
            self.payment_id = self.move_id._sm_print_cheque_payments()[:1]

    @api.onchange("payment_id")
    def _onchange_payment_id(self):
        if self.payment_id and not self.move_id:
            self.move_id = (self.payment_id.reconciled_invoice_ids | self.payment_id.reconciled_bill_ids)[:1]
        if self.payment_id:
            self.cheque_no = self.cheque_no or self.payment_id.payment_reference or self.payment_id.name or ""

    def action_print_cheque(self):
        self.ensure_one()
        if not self.payment_id:
            raise UserError(_("Select a payment first."))
        if not self.cheque_format_id:
            raise UserError(_("Select a cheque format first."))
        return self.env.ref("sm_print_cheque.action_report_cheque").report_action(self)

    def _sm_payment_amount(self):
        self.ensure_one()
        payment = self.payment_id
        amount = payment.amount
        currency = payment.currency_id or payment.company_id.currency_id
        value = f"{amount:,.2f}"
        if self.cheque_format_id.print_currency:
            value = f"{currency.symbol or currency.name} {value}"
        return self.cheque_format_id._sm_value_with_stars(value, self.cheque_format_id.print_amount_star)

    def _sm_partner_name(self):
        self.ensure_one()
        partner = self.payment_id.partner_id.display_name or ""
        title = self.partner_title or ""
        position = self.cheque_format_id.partner_title_position
        if title and position == "prefix":
            return f"{title} {partner}"
        if title and position == "suffix":
            return f"{partner} {title}"
        return partner

    def _sm_cheque_no(self):
        self.ensure_one()
        return self.cheque_no or self.payment_id.payment_reference or self.payment_id.name or ""

    def _sm_amount_words_lines(self):
        self.ensure_one()
        cheque_format = self.cheque_format_id
        words = self.payment_id.sm_amount_in_words or ""
        if cheque_format.print_only_word and words and "only" not in words.lower():
            words = f"{words} Only"
        words = cheque_format._sm_value_with_stars(words, cheque_format.print_words_star)
        split_after = max(0, cheque_format.split_words_after or 0)
        if not split_after:
            return [words, ""]
        parts = words.split()
        if len(parts) <= split_after:
            return [words, ""]
        return [" ".join(parts[:split_after]), " ".join(parts[split_after:])]

    def _sm_date_digits(self):
        self.ensure_one()
        cheque_format = self.cheque_format_id
        date_value = fields.Date.to_date(self.payment_id.date or fields.Date.context_today(self))
        year = str(date_value.year if cheque_format.year_format == "yyyy" else date_value.year % 100).zfill(
            4 if cheque_format.year_format == "yyyy" else 2
        )
        month = str(date_value.month).zfill(2)
        day = str(date_value.day).zfill(2)
        if cheque_format.date_format in ("dd_mm", "dd_mm_yyyy"):
            value = day + month + year
        else:
            value = month + day + year
        lefts = [
            cheque_format.date_first_left,
            cheque_format.date_second_left,
            cheque_format.date_third_left,
            cheque_format.date_fourth_left,
            cheque_format.date_fifth_left,
            cheque_format.date_sixth_left,
            cheque_format.date_seventh_left,
            cheque_format.date_eighth_left,
        ]
        return [
            {"char": char, "style": cheque_format._sm_style(cheque_format.date_top, left)}
            for char, left in zip(value[:len(lefts)], lefts)
        ]

    def _sm_payment_stub_lines(self):
        self.ensure_one()
        payment = self.payment_id
        invoices = payment.reconciled_invoice_ids | payment.reconciled_bill_ids
        if self.move_id:
            invoices |= self.move_id
        invoices = invoices.sorted(lambda move: (move.invoice_date or move.date, move.id))
        if not invoices:
            invoices = self.env["account.move"]
        if invoices:
            return [{
                "date": invoice.invoice_date or invoice.date,
                "type": "Receive" if payment.payment_type == "inbound" else "Payment",
                "reference": invoice.name,
                "payment": self._sm_format_money(payment.amount, payment.currency_id),
            } for invoice in invoices]
        return [{
            "date": payment.date,
            "type": "Receive" if payment.payment_type == "inbound" else "Payment",
            "reference": payment.name,
            "payment": self._sm_format_money(payment.amount, payment.currency_id),
        }]

    def _sm_journal_lines(self):
        self.ensure_one()
        move = self.move_id
        if not move:
            move = (self.payment_id.reconciled_invoice_ids | self.payment_id.reconciled_bill_ids)[:1]
        if not move:
            move = self.payment_id.move_id
        return move.line_ids.filtered(lambda line: line.account_id).sorted(lambda line: (line.sequence, line.id))

    def _sm_format_date(self, value):
        if not value:
            return ""
        date_value = fields.Date.to_date(value)
        return date_value.strftime("%m/%d/%Y")

    def _sm_format_money(self, amount, currency):
        symbol = (currency.symbol or currency.name or "").replace("\xa0", " ").strip()
        return f"{symbol} {amount:,.2f}".strip()
