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
Data models for New Order Batch

* :class:`NewOrderBatch`
* :class:`NewOrderBatchRow`
"""

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from wuttjamaican.db import model

from sideshow.db.model.orders import OrderMixin, OrderItemMixin


class NewOrderBatch(model.BatchMixin, OrderMixin, model.Base):
    """
    :term:`Batch <batch>` used for entering new :term:`orders <order>`
    into the system.  Each batch ultimately becomes an
    :class:`~sideshow.db.model.orders.Order`.

    See also :class:`~sideshow.batch.neworder.NewOrderBatchHandler`
    which is the default :term:`batch handler` for this :term:`batch
    type`.

    Generic batch attributes (undocumented below) are inherited from
    :class:`~wuttjamaican:wuttjamaican.db.model.batch.BatchMixin`.
    """

    __tablename__ = "sideshow_batch_neworder"
    __batchrow_class__ = "NewOrderBatchRow"

    batch_type = "neworder"
    """
    Official :term:`batch type` key.
    """

    @declared_attr
    def __table_args__(cls):  # pylint: disable=no-self-argument
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(
                ["local_customer_uuid"], ["sideshow_customer_local.uuid"]
            ),
            sa.ForeignKeyConstraint(
                ["pending_customer_uuid"], ["sideshow_customer_pending.uuid"]
            ),
        )

    STATUS_OK = 1

    STATUS = {
        STATUS_OK: "ok",
    }

    local_customer_uuid = sa.Column(model.UUID(), nullable=True)

    @declared_attr
    def local_customer(  # pylint: disable=no-self-argument,missing-function-docstring
        cls,
    ):
        return orm.relationship(
            "LocalCustomer",
            cascade_backrefs=False,
            back_populates="new_order_batches",
            doc="""
            Reference to the
            :class:`~sideshow.db.model.customers.LocalCustomer` record
            for the order, if applicable.

            See also :attr:`customer_id` and :attr:`pending_customer`.
            """,
        )

    pending_customer_uuid = sa.Column(model.UUID(), nullable=True)

    @declared_attr
    def pending_customer(  # pylint: disable=no-self-argument,missing-function-docstring
        cls,
    ):
        return orm.relationship(
            "PendingCustomer",
            cascade_backrefs=False,
            back_populates="new_order_batches",
            doc="""
            Reference to the
            :class:`~sideshow.db.model.customers.PendingCustomer`
            record for the order, if applicable.

            See also :attr:`customer_id` and :attr:`local_customer`.
            """,
        )


class NewOrderBatchRow(model.BatchRowMixin, OrderItemMixin, model.Base):
    """
    Row of data within a :class:`NewOrderBatch`.  Each row ultimately
    becomes an :class:`~sideshow.db.model.orders.OrderItem`.

    Generic row attributes (undocumented below) are inherited from
    :class:`~wuttjamaican:wuttjamaican.db.model.batch.BatchRowMixin`.
    """

    __tablename__ = "sideshow_batch_neworder_row"
    __batch_class__ = NewOrderBatch

    @declared_attr
    def __table_args__(cls):  # pylint: disable=no-self-argument
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(
                ["local_product_uuid"], ["sideshow_product_local.uuid"]
            ),
            sa.ForeignKeyConstraint(
                ["pending_product_uuid"], ["sideshow_product_pending.uuid"]
            ),
        )

    STATUS_OK = 1
    """
    This is the default value for :attr:`status_code`.  All rows are
    considered "OK" if they have either a :attr:`product_id` or
    :attr:`pending_product`.
    """

    STATUS_MISSING_PRODUCT = 2
    """
    Status code indicating the row has no :attr:`product_id` or
    :attr:`pending_product` set.
    """

    STATUS_MISSING_ORDER_QTY = 3
    """
    Status code indicating the row has no :attr:`order_qty` and/or
    :attr:`order_uom` set.
    """

    STATUS = {
        STATUS_OK: "ok",
        STATUS_MISSING_PRODUCT: "missing product",
        STATUS_MISSING_ORDER_QTY: "missing order qty/uom",
    }
    """
    Dict of possible status code -> label options.
    """

    local_product_uuid = sa.Column(model.UUID(), nullable=True)

    @declared_attr
    def local_product(  # pylint: disable=no-self-argument,missing-function-docstring
        cls,
    ):
        return orm.relationship(
            "LocalProduct",
            cascade_backrefs=False,
            back_populates="new_order_batch_rows",
            doc="""
            Reference to the
            :class:`~sideshow.db.model.products.LocalProduct` record
            for the order item, if applicable.

            See also :attr:`product_id` and :attr:`pending_product`.
            """,
        )

    pending_product_uuid = sa.Column(model.UUID(), nullable=True)

    @declared_attr
    def pending_product(  # pylint: disable=no-self-argument,missing-function-docstring
        cls,
    ):
        return orm.relationship(
            "PendingProduct",
            cascade_backrefs=False,
            back_populates="new_order_batch_rows",
            doc="""
            Reference to the
            :class:`~sideshow.db.model.products.PendingProduct` record
            for the order item, if applicable.

            See also :attr:`product_id` and :attr:`local_product`.
            """,
        )

    def __str__(self):
        return str(self.pending_product or self.product_description or "")
