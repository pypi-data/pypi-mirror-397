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
Web Utility Functions
"""


def make_new_order_batches_grid(request, **kwargs):
    """
    Make and return the grid for the New Order Batches field.
    """
    config = request.wutta_config
    app = config.get_app()
    model = app.model
    web = app.get_web_handler()

    if "key" not in kwargs:
        route_prefix = kwargs.pop("route_prefix")
        kwargs["key"] = f"{route_prefix}.view.new_order_batches"

    kwargs.setdefault("model_class", model.NewOrderBatch)
    kwargs.setdefault(
        "columns",
        [
            "id",
            "total_price",
            "created",
            "created_by",
            "executed",
        ],
    )
    kwargs.setdefault("labels", {"id": "Batch ID"})
    kwargs.setdefault("renderers", {"id": "batch_id", "total_price": "currency"})
    grid = web.make_grid(request, **kwargs)

    if request.has_perm("neworder_batches.view"):

        def view_url(batch, i):  # pylint: disable=unused-argument
            return request.route_url("neworder_batches.view", uuid=batch.uuid)

        grid.add_action("view", icon="eye", url=view_url)
        grid.set_link("id")

    return grid


def make_orders_grid(request, **kwargs):
    """
    Make and return the grid for the Orders field.
    """
    config = request.wutta_config
    app = config.get_app()
    model = app.model
    web = app.get_web_handler()

    if "key" not in kwargs:
        route_prefix = kwargs.pop("route_prefix")
        kwargs["key"] = f"{route_prefix}.view.orders"

    kwargs.setdefault("model_class", model.Order)
    kwargs.setdefault(
        "columns",
        [
            "order_id",
            "total_price",
            "created",
            "created_by",
        ],
    )
    kwargs.setdefault("labels", {"order_id": "Order ID"})
    kwargs.setdefault("renderers", {"total_price": "currency"})
    grid = web.make_grid(request, **kwargs)

    if request.has_perm("orders.view"):

        def view_url(order, i):  # pylint: disable=unused-argument
            return request.route_url("orders.view", uuid=order.uuid)

        grid.add_action("view", icon="eye", url=view_url)
        grid.set_link("order_id")

    return grid
