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
Views for Products
"""

from wuttaweb.views import MasterView
from wuttaweb.forms.schema import WuttaMoney, WuttaQuantity

from sideshow.enum import PendingProductStatus
from sideshow.db.model import LocalProduct, PendingProduct
from sideshow.web.views.shared import PendingMixin
from sideshow.web.util import make_new_order_batches_grid, make_orders_grid


class LocalProductView(MasterView):  # pylint: disable=abstract-method
    """
    Master view for :class:`~sideshow.db.model.products.LocalProduct`;
    route prefix is ``local_products``.

    Notable URLs provided by this class:

    * ``/local/products/``
    * ``/local/products/new``
    * ``/local/products/XXX``
    * ``/local/products/XXX/edit``
    * ``/local/products/XXX/delete``
    """

    model_class = LocalProduct
    model_title = "Local Product"
    route_prefix = "local_products"
    url_prefix = "/local/products"

    labels = {
        "external_id": "External ID",
        "department_id": "Department ID",
    }

    grid_columns = [
        "scancode",
        "brand_name",
        "description",
        "size",
        "department_name",
        "special_order",
        "case_size",
        "unit_cost",
        "unit_price_reg",
    ]

    sort_defaults = "scancode"

    # pylint: disable=duplicate-code
    form_fields = [
        "external_id",
        "scancode",
        "brand_name",
        "description",
        "size",
        "department_id",
        "department_name",
        "special_order",
        "vendor_name",
        "vendor_item_code",
        "case_size",
        "unit_cost",
        "unit_price_reg",
        "notes",
        "orders",
        "new_order_batches",
    ]
    # pylint: enable=duplicate-code

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)

        # unit_cost
        g.set_renderer("unit_cost", "currency", scale=4)

        # unit_price_reg
        g.set_label("unit_price_reg", "Reg. Price", column_only=True)
        g.set_renderer("unit_price_reg", "currency")

        # links
        g.set_link("scancode")
        g.set_link("brand_name")
        g.set_link("description")
        g.set_link("size")

    def configure_form(self, form):  # pylint: disable=empty-docstring
        """ """
        f = form
        super().configure_form(f)
        product = f.model_instance

        # external_id
        if self.creating:
            f.remove("external_id")
        else:
            f.set_readonly("external_id")

        # TODO: should not have to explicitly mark these nodes
        # as required=False.. i guess i do for now b/c i am
        # totally overriding the node from colanderlachemy

        # case_size
        f.set_node("case_size", WuttaQuantity(self.request))
        f.set_required("case_size", False)

        # unit_cost
        f.set_node("unit_cost", WuttaMoney(self.request, scale=4))
        f.set_required("unit_cost", False)

        # unit_price_reg
        f.set_node("unit_price_reg", WuttaMoney(self.request))
        f.set_required("unit_price_reg", False)

        # notes
        f.set_widget("notes", "notes")

        # orders
        if self.creating or self.editing:
            f.remove("orders")
        else:
            f.set_grid("orders", self.make_orders_grid(product))

        # new_order_batches
        if self.creating or self.editing:
            f.remove("new_order_batches")
        else:
            f.set_grid("new_order_batches", self.make_new_order_batches_grid(product))

    def make_orders_grid(self, product):
        """
        Make and return the grid for the Orders field.
        """
        orders = {item.order for item in product.order_items}
        orders = sorted(orders, key=lambda order: order.order_id)

        return make_orders_grid(
            self.request, route_prefix=self.get_route_prefix(), data=orders
        )

    def make_new_order_batches_grid(self, product):
        """
        Make and return the grid for the New Order Batches field.
        """
        batches = {row.batch for row in product.new_order_batch_rows}
        batches = sorted(batches, key=lambda batch: batch.id)

        return make_new_order_batches_grid(
            self.request,
            route_prefix=self.get_route_prefix(),
            data=batches,
        )


class PendingProductView(PendingMixin, MasterView):  # pylint: disable=abstract-method
    """
    Master view for
    :class:`~sideshow.db.model.products.PendingProduct`; route
    prefix is ``pending_products``.

    Notable URLs provided by this class:

    * ``/pending/products/``
    * ``/pending/products/new``
    * ``/pending/products/XXX``
    * ``/pending/products/XXX/edit``
    * ``/pending/products/XXX/delete``
    """

    model_class = PendingProduct
    model_title = "Pending Product"
    route_prefix = "pending_products"
    url_prefix = "/pending/products"

    labels = {
        "department_id": "Department ID",
        "product_id": "Product ID",
    }

    grid_columns = [
        "scancode",
        "department_name",
        "brand_name",
        "description",
        "size",
        "unit_cost",
        "case_size",
        "unit_price_reg",
        "special_order",
        "status",
        "created",
        "created_by",
    ]

    sort_defaults = ("created", "desc")

    filter_defaults = {
        "status": {"active": True, "value": PendingProductStatus.READY.name},
    }

    form_fields = [
        "product_id",
        "scancode",
        "department_id",
        "department_name",
        "brand_name",
        "description",
        "size",
        "vendor_name",
        "vendor_item_code",
        "unit_cost",
        "case_size",
        "unit_price_reg",
        "special_order",
        "notes",
        "created",
        "created_by",
        "orders",
        "new_order_batches",
    ]

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)
        enum = self.app.enum

        # unit_cost
        g.set_renderer("unit_cost", "currency", scale=4)

        # unit_price_reg
        g.set_label("unit_price_reg", "Reg. Price", column_only=True)
        g.set_renderer("unit_price_reg", "currency")

        # status
        g.set_enum("status", enum.PendingProductStatus)

        # links
        g.set_link("scancode")
        g.set_link("brand_name")
        g.set_link("description")
        g.set_link("size")

    def grid_row_class(  # pylint: disable=unused-argument,empty-docstring
        self, product, data, i
    ):
        """ """
        enum = self.app.enum
        if product.status == enum.PendingProductStatus.IGNORED:
            return "has-background-warning"
        return None

    def configure_form(self, form):  # pylint: disable=empty-docstring
        """ """
        f = form
        super().configure_form(f)

        self.configure_form_pending(f)

        # product_id
        if self.creating:
            f.remove("product_id")
        else:
            f.set_readonly("product_id")

        # unit_price_reg
        f.set_node("unit_price_reg", WuttaMoney(self.request))

        # notes
        f.set_widget("notes", "notes")

    def make_orders_grid(self, product):
        """
        Make and return the grid for the Orders field.
        """
        orders = {item.order for item in product.order_items}
        orders = sorted(orders, key=lambda order: order.order_id)

        return make_orders_grid(
            self.request, route_prefix=self.get_route_prefix(), data=orders
        )

    def make_new_order_batches_grid(self, product):
        """
        Make and return the grid for the New Order Batches field.
        """
        batches = {row.batch for row in product.new_order_batch_rows}
        batches = sorted(batches, key=lambda batch: batch.id)

        return make_new_order_batches_grid(
            self.request,
            route_prefix=self.get_route_prefix(),
            data=batches,
        )

    def get_template_context(self, context):  # pylint: disable=empty-docstring
        """ """
        enum = self.app.enum

        if self.viewing:
            product = context["instance"]
            if product.status == enum.PendingProductStatus.READY and self.has_any_perm(
                "resolve", "ignore"
            ):
                handler = self.app.get_batch_handler("neworder")
                context["use_local_products"] = handler.use_local_products()

        return context

    def delete_instance(self, obj):  # pylint: disable=empty-docstring
        """ """
        product = obj

        # avoid deleting if still referenced by new order batch(es)
        for row in product.new_order_batch_rows:
            if not row.batch.executed:
                model_title = self.get_model_title()
                self.request.session.flash(
                    f"Cannot delete {model_title} still attached "
                    "to New Order Batch(es)",
                    "warning",
                )
                raise self.redirect(self.get_action_url("view", product))

        # go ahead and delete per usual
        super().delete_instance(product)

    def resolve(self):
        """
        View to "resolve" a :term:`pending product` with the real
        :term:`external product`.

        This view requires POST, with ``product_id`` referencing the
        desired external product.

        It will call
        :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.get_product_info_external()`
        to fetch product info, then with that it calls
        :meth:`~sideshow.orders.OrderHandler.resolve_pending_product()`
        to update related :term:`order items <order item>` etc.

        See also :meth:`ignore()`.
        """
        enum = self.app.enum
        session = self.Session()
        product = self.get_instance()

        if product.status != enum.PendingProductStatus.READY:
            self.request.session.flash(
                "pending product does not have 'ready' status!", "error"
            )
            return self.redirect(self.get_action_url("view", product))

        product_id = self.request.POST.get("product_id")
        if not product_id:
            self.request.session.flash("must specify valid product_id", "error")
            return self.redirect(self.get_action_url("view", product))

        batch_handler = self.app.get_batch_handler("neworder")
        order_handler = self.app.get_order_handler()

        info = batch_handler.get_product_info_external(session, product_id)
        order_handler.resolve_pending_product(product, info, self.request.user)

        return self.redirect(self.get_action_url("view", product))

    def ignore(self):
        """
        View to "ignore" a :term:`pending product` so the user is no
        longer prompted to resolve it.

        This view requires POST; it merely sets the product status to
        "ignored".

        See also :meth:`resolve()`.
        """
        enum = self.app.enum
        product = self.get_instance()

        if product.status != enum.PendingProductStatus.READY:
            self.request.session.flash(
                "pending product does not have 'ready' status!", "error"
            )
            return self.redirect(self.get_action_url("view", product))

        product.status = enum.PendingProductStatus.IGNORED
        return self.redirect(self.get_action_url("view", product))

    @classmethod
    def defaults(cls, config):  # pylint: disable=empty-docstring
        """ """
        cls._defaults(config)
        cls._pending_product_defaults(config)

    @classmethod
    def _pending_product_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        model_title = cls.get_model_title()

        # resolve
        config.add_wutta_permission(
            permission_prefix, f"{permission_prefix}.resolve", f"Resolve {model_title}"
        )
        config.add_route(
            f"{route_prefix}.resolve",
            f"{instance_url_prefix}/resolve",
            request_method="POST",
        )
        config.add_view(
            cls,
            attr="resolve",
            route_name=f"{route_prefix}.resolve",
            permission=f"{permission_prefix}.resolve",
        )

        # ignore
        config.add_wutta_permission(
            permission_prefix, f"{permission_prefix}.ignore", f"Ignore {model_title}"
        )
        config.add_route(
            f"{route_prefix}.ignore",
            f"{instance_url_prefix}/ignore",
            request_method="POST",
        )
        config.add_view(
            cls,
            attr="ignore",
            route_name=f"{route_prefix}.ignore",
            permission=f"{permission_prefix}.ignore",
        )


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    base = globals()

    LocalProductView = kwargs.get(  # pylint: disable=redefined-outer-name,invalid-name
        "LocalProductView", base["LocalProductView"]
    )
    LocalProductView.defaults(config)

    PendingProductView = (  # pylint: disable=redefined-outer-name,invalid-name
        kwargs.get("PendingProductView", base["PendingProductView"])
    )
    PendingProductView.defaults(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
