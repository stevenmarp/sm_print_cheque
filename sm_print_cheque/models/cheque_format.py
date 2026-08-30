import base64

from odoo import api, fields, models
from odoo.modules.module import get_module_path


class SmChequeFormat(models.Model):
    _name = "sm.cheque.format"
    _description = "Cheque Format"
    _order = "default_template desc, name"

    name = fields.Char(string="Cheque Name", required=True)
    font_size = fields.Float(default=13.0, required=True)
    color = fields.Char(default="#000", required=True)
    default_template = fields.Boolean(default=False)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    page_width = fields.Float(default=216.0, required=True)
    page_height = fields.Float(default=297.0, required=True)
    print_cheque_background = fields.Boolean(string="Print Cheque Background", default=True)

    print_partner = fields.Boolean(default=True)
    partner_font_bold = fields.Boolean(default=False)
    partner_title_position = fields.Selection(
        [("none", "None"), ("prefix", "Prefix"), ("suffix", "Suffix")],
        default="prefix",
        required=True,
    )
    partner_top = fields.Float(default=130.0)
    partner_left = fields.Float(default=70.0)

    print_customer_address = fields.Boolean(default=False)
    address_top = fields.Float(default=100.0)
    address_left = fields.Float(default=70.0)

    print_date = fields.Boolean(default=True)
    date_separator = fields.Char(default="/")
    date_format = fields.Selection(
        [("mm_dd", "MM DD"), ("dd_mm", "DD MM"), ("mm_dd_yyyy", "MM DD YYYY"), ("dd_mm_yyyy", "DD MM YYYY")],
        default="mm_dd",
        required=True,
    )
    year_format = fields.Selection([("yy", "YY"), ("yyyy", "YYYY")], default="yy", required=True)
    date_top = fields.Float(default=92.0)
    date_first_left = fields.Float(default=550.0)
    date_second_left = fields.Float(default=560.0)
    date_third_left = fields.Float(default=590.0)
    date_fourth_left = fields.Float(default=600.0)
    date_fifth_left = fields.Float(default=625.0)
    date_sixth_left = fields.Float(default=635.0)
    date_seventh_left = fields.Float(default=645.0)
    date_eighth_left = fields.Float(default=655.0)

    print_amount = fields.Boolean(default=True)
    print_currency = fields.Boolean(default=True)
    print_amount_star = fields.Boolean(string="Print Amount Star", default=True)
    amount_top = fields.Float(default=174.0)
    amount_left = fields.Float(default=552.0)

    print_amount_words = fields.Boolean(default=True)
    print_words_star = fields.Boolean(string="Print Words Star", default=True)
    amount_words_font_bold = fields.Boolean(string="Font Bold", default=False)
    split_words_after = fields.Integer(default=7)
    words_first_top = fields.Float(default=152.0)
    words_first_left = fields.Float(default=70.0)
    words_second_top = fields.Float(default=176.0)
    words_second_left = fields.Float(default=70.0)
    decimal_format = fields.Selection([("default", "Default"), ("fraction", "Fraction")], default="default")
    print_only_word = fields.Boolean(string="Print word 'Only'", default=True)

    print_company = fields.Boolean(default=True)
    company_top = fields.Float(default=266.0)
    company_left = fields.Float(default=560.0)

    print_cheque_no = fields.Boolean(default=True)
    cheque_no_top = fields.Float(default=58.0)
    cheque_no_left = fields.Float(default=510.0)

    print_ac_pay = fields.Boolean(string="Print A/C PAY", default=True)
    ac_pay_top = fields.Float(default=104.0)
    ac_pay_left = fields.Float(default=70.0)

    print_first_signature = fields.Boolean(string="Print First Signature", default=True)
    first_signature_top = fields.Float(default=238.0)
    first_signature_left = fields.Float(default=500.0)

    print_second_signature = fields.Boolean(string="Print Second Signature", default=False)
    second_signature_top = fields.Float(default=350.0)
    second_signature_left = fields.Float(default=510.0)

    print_free_text_one = fields.Boolean(default=True)
    free_text_one_top = fields.Float(default=250.0)
    free_text_one_left = fields.Float(default=70.0)

    print_free_text_two = fields.Boolean(default=True)
    free_text_two_top = fields.Float(default=250.0)
    free_text_two_left = fields.Float(default=300.0)

    print_stub = fields.Boolean(default=True)
    stub_top = fields.Float(default=360.0)
    stub_left = fields.Float(default=35.0)

    @api.constrains("default_template", "company_id")
    def _check_default_template(self):
        for cheque_format in self.filtered("default_template"):
            others = self.search([
                ("id", "!=", cheque_format.id),
                ("company_id", "=", cheque_format.company_id.id),
                ("default_template", "=", True),
            ])
            others.default_template = False

    def _sm_style(self, top, left, bold=False, extra=""):
        self.ensure_one()
        weight = "font-weight:700;" if bold else ""
        return (
            "position:absolute; "
            f"top:{top}px; left:{left}px; "
            f"font-size:{self.font_size}px; color:{self.color}; "
            f"{weight}{extra}"
        )

    def _sm_value_with_stars(self, value, enabled=True):
        return f"**{value}**" if enabled else value

    def _sm_background_data_uri(self):
        module_path = get_module_path("sm_print_cheque")
        if not module_path:
            return ""
        path = f"{module_path}/static/src/img/cheque_background.png"
        with open(path, "rb") as background:
            encoded = base64.b64encode(background.read()).decode()
        return f"data:image/png;base64,{encoded}"
