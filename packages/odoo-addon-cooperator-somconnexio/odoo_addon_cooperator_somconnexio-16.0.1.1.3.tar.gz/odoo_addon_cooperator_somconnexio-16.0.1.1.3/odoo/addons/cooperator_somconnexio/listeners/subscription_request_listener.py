from odoo.addons.component.core import Component


class SubscriptionRequest(Component):
    _name = "partner.subscription.request.listener"
    _inherit = "base.event.listener"
    _apply_on = [
        "subscription.request",
    ]

    def on_record_create(self, record, fields=None):
        if "source" in fields and record.source == "website_request_cooperator":
            if record.state == "draft":
                record.validate_subscription_request()
