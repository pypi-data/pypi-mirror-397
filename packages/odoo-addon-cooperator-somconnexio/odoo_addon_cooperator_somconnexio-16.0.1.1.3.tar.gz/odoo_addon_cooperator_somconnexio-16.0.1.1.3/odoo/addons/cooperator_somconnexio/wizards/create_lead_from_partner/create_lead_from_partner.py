from odoo import models


class CreateLeadFromPartnerWizard(models.TransientModel):
    _inherit = "partner.create.lead.wizard"

    def _get_available_categories(self):
        available_categories = super()._get_available_categories()
        coop_available_categories = self.env["product.category"]

        if self.partner_id.coop_sponsee:
            sc = self.env["coop.agreement"].search([("code", "=", "SC")])
            sc_product_templs = sc.products
            coop_available_categories = sc_product_templs.mapped("categ_id")
        elif self.partner_id.coop_agreement:
            product_templs = self.partner_id.coop_agreement_id.products
            coop_available_categories = product_templs.mapped("categ_id")
        else:
            return available_categories

        return coop_available_categories & available_categories
