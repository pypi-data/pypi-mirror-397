from odoo.addons.component.tests.common import ComponentMixin
from odoo.tests.common import TransactionCase


class TestSubscriptionRequestListener(TransactionCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestSubscriptionRequestListener, cls).setUpClass()
        cls.setUpComponent()

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        ComponentMixin.setUp(self)

        partner = self.browse_ref("cooperator_somconnexio.res_sponsored_partner_1_demo")
        products = self.env["product.product"].search(
            [
                ("is_share", "=", True),
                ("default_share_product", "=", True),
                ("by_individual", "=", not partner.is_company),
            ]
        )
        self.website_params = {
            "partner_id": partner.id,
            "vat": partner.vat,
            "share_product_id": products[0].id,
            "ordered_parts": 1,
            "user_id": self.env.uid,
            "email": partner.email,
            "source": "website_request_cooperator",
            "firstname": partner.firstname,
            "lastname": partner.lastname,
            "address": partner.street,
            "zip_code": partner.zip,
            "city": partner.city,
            "country_id": partner.country_id.id,
            "lang": partner.lang,
            "is_company": partner.is_company,
            "iban": partner.bank_ids[0].acc_number,
            "payment_type": "split",
        }

    def test_sub_req_is_validated(self):
        sub_req = self.env["subscription.request"].create(self.website_params)
        self.assertEqual(sub_req.state, "done")

    def test_sub_req_is_not_validated(self):
        test_params = self.website_params.copy()
        test_params["source"] = "crm"
        sub_req = self.env["subscription.request"].create(test_params)
        self.assertEqual(sub_req.state, "draft")
