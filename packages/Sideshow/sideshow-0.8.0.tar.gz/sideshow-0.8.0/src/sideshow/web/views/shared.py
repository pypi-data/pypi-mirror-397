# -*- coding: utf-8; -*-
################################################################################
#
#  Sideshow -- Case/Special Order Tracker
#  Copyright © 2024-2025 Lance Edgar
#
#  This file is part of Sideshow.
#
#  Sideshow is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Sideshow is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Sideshow.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Shared View Logic
"""

from wuttaweb.forms.schema import UserRef


class PendingMixin:  # pylint: disable=too-few-public-methods
    """
    Mixin class with logic shared by Pending Customer and Pending
    Product views.
    """

    def configure_form_pending(self, form):  # pylint: disable=empty-docstring
        """ """
        f = form
        obj = f.model_instance

        # created
        if self.creating:
            f.remove("created")
        else:
            f.set_readonly("created")

        # created_by
        if self.creating:
            f.remove("created_by")
        else:
            f.set_node("created_by", UserRef(self.request))
            f.set_readonly("created_by")

        # orders
        if self.creating or self.editing:
            f.remove("orders")
        else:
            f.set_grid("orders", self.make_orders_grid(obj))

        # new_order_batches
        if self.creating or self.editing:
            f.remove("new_order_batches")
        else:
            f.set_grid("new_order_batches", self.make_new_order_batches_grid(obj))
