{
    "name": "Dynamic Print Cheque",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Print configurable cheques from invoices and payments with cheque format positioning, amount in words, stubs and journal lines",
    "description": """
Print Cheque for Odoo 19
========================

Print configurable cheques from invoices and payments. Create reusable cheque
formats, position each printed value, open a print wizard, and print a full
cheque report with amount in words, cheque number, free text, signatures, stub
lines and journal entry details.
    """,
    "author": "Steven Marp",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Steven Marp",
    "license": "OPL-1",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "data/cheque_format_data.xml",
        "report/cheque_paperformat.xml",
        "report/cheque_templates.xml",
        "report/cheque_report.xml",
        "views/cheque_format_views.xml",
        "views/print_cheque_wizard_views.xml",
        "views/account_move_views.xml",
        "views/account_payment_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": [
        "static/description/banner.gif",
        "static/description/icon.png",
        "static/description/print_cheque_01_format_settings.png",
        "static/description/print_cheque_02_amount_words_settings.png",
        "static/description/print_cheque_03_stub_settings.png",
        "static/description/print_cheque_04_print_wizard.png",
        "static/description/print_cheque_05_cheque_output.png",
        "static/description/print_cheque_06_cheque_output.png",
    ],
    "price": 36.00,
    "currency": "USD",
}
