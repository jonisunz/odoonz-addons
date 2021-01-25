# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

class StockQuantityHistory(models.TransientModel):

    _inherit = "stock.quantity.history"

    def open_at_date(self):
        if not self.env.context.get("valuation"):
            return super(StockQuantityHistory, self).open_at_date()
        action = super(StockQuantityHistory, self).open_at_date()
        context = dict(company_owned=True, owner_id=False)
        # if self.compute_at_date:
        #     context.update(to_date=self.date)
        product_ids = [
            item["product_id"][0]
            for item in self.env["stock.move"].read_group(
                [("date", "<=", self.inventory_datetime), ("state", "=", "done")],
                ["product_id"],
                ["product_id"],
                orderby="id",
            )
        ]
        products = (
            self.env["product.product"]
            .browse(product_ids)
            .with_context(**context)
            .filtered(lambda s: s.type == "product" and s.qty_available)
        )
        if products:
            action["domain"] = "[('id', 'in', %s)]" % products.ids
        return action
