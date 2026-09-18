from odoo import models


class TierReview(models.Model):
    _inherit = "tier.review"

    def _get_reviewers(self):
        reviewers = super()._get_reviewers()
        self.ensure_one()
        if self.model != "hr.expense.sheet":
            return reviewers

        resource = self.env[self.model].browse(self.res_id)
        if not resource:
            return reviewers
        if not hasattr(resource, "_get_tier_review_override_users"):
            return reviewers
        return resource._get_tier_review_override_users(self, reviewers)
