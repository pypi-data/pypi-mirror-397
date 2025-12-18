"""drop time zones

Revision ID: 9f2ff39f4743
Revises: fd8a2527bd30
Create Date: 2025-12-15 15:14:38.281566

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util
from sqlalchemy.dialects import postgresql
from wuttjamaican.util import make_utc

# revision identifiers, used by Alembic.
revision: str = "9f2ff39f4743"
down_revision: Union[str, None] = "fd8a2527bd30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # sideshow_batch_neworder.created
    op.add_column(
        "sideshow_batch_neworder",
        sa.Column("created_new", sa.DateTime(), nullable=True),
    )
    sideshow_batch_neworder = sa.sql.table(
        "sideshow_batch_neworder",
        sa.sql.column("uuid"),
        sa.sql.column("created"),
        sa.sql.column("created_new"),
    )
    cursor = op.get_bind().execute(sideshow_batch_neworder.select())
    for row in cursor.fetchall():
        op.get_bind().execute(
            sideshow_batch_neworder.update()
            .where(sideshow_batch_neworder.c.uuid == row.uuid)
            .values({"created_new": make_utc(row.created)})
        )
    op.drop_column("sideshow_batch_neworder", "created")
    op.alter_column(
        "sideshow_batch_neworder",
        "created_new",
        new_column_name="created",
        nullable=False,
        existing_type=sa.DateTime(),
        existing_nullable=True,
    )

    # sideshow_batch_neworder.executed
    op.add_column(
        "sideshow_batch_neworder",
        sa.Column("executed_new", sa.DateTime(), nullable=True),
    )
    sideshow_batch_neworder = sa.sql.table(
        "sideshow_batch_neworder",
        sa.sql.column("uuid"),
        sa.sql.column("executed"),
        sa.sql.column("executed_new"),
    )
    cursor = op.get_bind().execute(sideshow_batch_neworder.select())
    for row in cursor.fetchall():
        if row.executed:
            op.get_bind().execute(
                sideshow_batch_neworder.update()
                .where(sideshow_batch_neworder.c.uuid == row.uuid)
                .values({"executed_new": make_utc(row.executed)})
            )
    op.drop_column("sideshow_batch_neworder", "executed")
    op.alter_column(
        "sideshow_batch_neworder",
        "executed_new",
        new_column_name="executed",
        existing_type=sa.DateTime(),
        existing_nullable=True,
    )

    # sideshow_batch_neworder_row.modified
    op.add_column(
        "sideshow_batch_neworder_row",
        sa.Column("modified_new", sa.DateTime(), nullable=True),
    )
    sideshow_batch_neworder_row = sa.sql.table(
        "sideshow_batch_neworder_row",
        sa.sql.column("uuid"),
        sa.sql.column("modified"),
        sa.sql.column("modified_new"),
    )
    cursor = op.get_bind().execute(sideshow_batch_neworder_row.select())
    for row in cursor.fetchall():
        if row.modified:
            op.get_bind().execute(
                sideshow_batch_neworder_row.update()
                .where(sideshow_batch_neworder_row.c.uuid == row.uuid)
                .values({"modified_new": make_utc(row.modified)})
            )
    op.drop_column("sideshow_batch_neworder_row", "modified")
    op.alter_column(
        "sideshow_batch_neworder_row",
        "modified_new",
        new_column_name="modified",
        existing_type=sa.DateTime(),
        existing_nullable=True,
    )

    # sideshow_batch_neworder_row.sale_ends
    op.add_column(
        "sideshow_batch_neworder_row",
        sa.Column("sale_ends_new", sa.DateTime(), nullable=True),
    )
    sideshow_batch_neworder_row = sa.sql.table(
        "sideshow_batch_neworder_row",
        sa.sql.column("uuid"),
        sa.sql.column("sale_ends"),
        sa.sql.column("sale_ends_new"),
    )
    cursor = op.get_bind().execute(sideshow_batch_neworder_row.select())
    for row in cursor.fetchall():
        if row.sale_ends:
            op.get_bind().execute(
                sideshow_batch_neworder_row.update()
                .where(sideshow_batch_neworder_row.c.uuid == row.uuid)
                .values({"sale_ends_new": make_utc(row.sale_ends)})
            )
    op.drop_column("sideshow_batch_neworder_row", "sale_ends")
    op.alter_column(
        "sideshow_batch_neworder_row",
        "sale_ends_new",
        new_column_name="sale_ends",
        existing_type=sa.DateTime(),
        existing_nullable=True,
    )

    # sideshow_customer_pending.created
    op.add_column(
        "sideshow_customer_pending",
        sa.Column("created_new", sa.DateTime(), nullable=True),
    )
    sideshow_customer_pending = sa.sql.table(
        "sideshow_customer_pending",
        sa.sql.column("uuid"),
        sa.sql.column("created"),
        sa.sql.column("created_new"),
    )
    cursor = op.get_bind().execute(sideshow_customer_pending.select())
    for row in cursor.fetchall():
        op.get_bind().execute(
            sideshow_customer_pending.update()
            .where(sideshow_customer_pending.c.uuid == row.uuid)
            .values({"created_new": make_utc(row.created)})
        )
    op.drop_column("sideshow_customer_pending", "created")
    op.alter_column(
        "sideshow_customer_pending",
        "created_new",
        new_column_name="created",
        nullable=False,
        existing_type=sa.DateTime(),
        existing_nullable=True,
    )

    # sideshow_order.created
    op.add_column(
        "sideshow_order",
        sa.Column("created_new", sa.DateTime(), nullable=True),
    )
    sideshow_order = sa.sql.table(
        "sideshow_order",
        sa.sql.column("uuid"),
        sa.sql.column("created"),
        sa.sql.column("created_new"),
    )
    cursor = op.get_bind().execute(sideshow_order.select())
    for row in cursor.fetchall():
        op.get_bind().execute(
            sideshow_order.update()
            .where(sideshow_order.c.uuid == row.uuid)
            .values({"created_new": make_utc(row.created)})
        )
    op.drop_column("sideshow_order", "created")
    op.alter_column(
        "sideshow_order",
        "created_new",
        new_column_name="created",
        nullable=False,
        existing_type=sa.DateTime(),
        existing_nullable=True,
    )

    # sideshow_order_item.sale_ends
    op.add_column(
        "sideshow_order_item",
        sa.Column("sale_ends_new", sa.DateTime(), nullable=True),
    )
    sideshow_order_item = sa.sql.table(
        "sideshow_order_item",
        sa.sql.column("uuid"),
        sa.sql.column("sale_ends"),
        sa.sql.column("sale_ends_new"),
    )
    cursor = op.get_bind().execute(sideshow_order_item.select())
    for row in cursor.fetchall():
        if row.sale_ends:
            op.get_bind().execute(
                sideshow_order_item.update()
                .where(sideshow_order_item.c.uuid == row.uuid)
                .values({"sale_ends_new": make_utc(row.sale_ends)})
            )
    op.drop_column("sideshow_order_item", "sale_ends")
    op.alter_column(
        "sideshow_order_item",
        "sale_ends_new",
        new_column_name="sale_ends",
        existing_type=sa.DateTime(),
        existing_nullable=True,
    )

    # sideshow_order_item_event.occurred
    op.add_column(
        "sideshow_order_item_event",
        sa.Column("occurred_new", sa.DateTime(), nullable=True),
    )
    sideshow_order_item_event = sa.sql.table(
        "sideshow_order_item_event",
        sa.sql.column("uuid"),
        sa.sql.column("occurred"),
        sa.sql.column("occurred_new"),
    )
    cursor = op.get_bind().execute(sideshow_order_item_event.select())
    for row in cursor.fetchall():
        op.get_bind().execute(
            sideshow_order_item_event.update()
            .where(sideshow_order_item_event.c.uuid == row.uuid)
            .values({"occurred_new": make_utc(row.occurred)})
        )
    op.drop_column("sideshow_order_item_event", "occurred")
    op.alter_column(
        "sideshow_order_item_event",
        "occurred_new",
        new_column_name="occurred",
        nullable=False,
        existing_type=sa.DateTime(),
        existing_nullable=True,
    )

    # sideshow_product_pending.created
    op.add_column(
        "sideshow_product_pending",
        sa.Column("created_new", sa.DateTime(), nullable=True),
    )
    sideshow_product_pending = sa.sql.table(
        "sideshow_product_pending",
        sa.sql.column("uuid"),
        sa.sql.column("created"),
        sa.sql.column("created_new"),
    )
    cursor = op.get_bind().execute(sideshow_product_pending.select())
    for row in cursor.fetchall():
        op.get_bind().execute(
            sideshow_product_pending.update()
            .where(sideshow_product_pending.c.uuid == row.uuid)
            .values({"created_new": make_utc(row.created)})
        )
    op.drop_column("sideshow_product_pending", "created")
    op.alter_column(
        "sideshow_product_pending",
        "created_new",
        new_column_name="created",
        nullable=False,
        existing_type=sa.DateTime(),
        existing_nullable=True,
    )


def downgrade() -> None:

    # sideshow_product_pending.created
    op.add_column(
        "sideshow_product_pending",
        sa.Column("created_old", sa.DateTime(timezone=True), nullable=True),
    )
    sideshow_product_pending = sa.sql.table(
        "sideshow_product_pending",
        sa.sql.column("uuid"),
        sa.sql.column("created"),
        sa.sql.column("created_old"),
    )
    cursor = op.get_bind().execute(sideshow_product_pending.select())
    for row in cursor.fetchall():
        op.get_bind().execute(
            sideshow_product_pending.update()
            .where(sideshow_product_pending.c.uuid == row.uuid)
            .values({"created_old": row.created})
        )
    op.drop_column("sideshow_product_pending", "created")
    op.alter_column(
        "sideshow_product_pending",
        "created_old",
        new_column_name="created",
        nullable=False,
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )

    # sideshow_order_item_event.occurred
    op.add_column(
        "sideshow_order_item_event",
        sa.Column("occurred_old", sa.DateTime(timezone=True), nullable=True),
    )
    sideshow_order_item_event = sa.sql.table(
        "sideshow_order_item_event",
        sa.sql.column("uuid"),
        sa.sql.column("occurred"),
        sa.sql.column("occurred_old"),
    )
    cursor = op.get_bind().execute(sideshow_order_item_event.select())
    for row in cursor.fetchall():
        op.get_bind().execute(
            sideshow_order_item_event.update()
            .where(sideshow_order_item_event.c.uuid == row.uuid)
            .values({"occurred_old": row.occurred})
        )
    op.drop_column("sideshow_order_item_event", "occurred")
    op.alter_column(
        "sideshow_order_item_event",
        "occurred_old",
        new_column_name="occurred",
        nullable=False,
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )

    # sideshow_order_item.sale_ends
    op.add_column(
        "sideshow_order_item",
        sa.Column("sale_ends_old", sa.DateTime(timezone=True), nullable=True),
    )
    sideshow_order_item = sa.sql.table(
        "sideshow_order_item",
        sa.sql.column("uuid"),
        sa.sql.column("sale_ends"),
        sa.sql.column("sale_ends_old"),
    )
    cursor = op.get_bind().execute(sideshow_order_item.select())
    for row in cursor.fetchall():
        if row.sale_ends:
            op.get_bind().execute(
                sideshow_order_item.update()
                .where(sideshow_order_item.c.uuid == row.uuid)
                .values({"sale_ends_old": row.sale_ends})
            )
    op.drop_column("sideshow_order_item", "sale_ends")
    op.alter_column(
        "sideshow_order_item",
        "sale_ends_old",
        new_column_name="sale_ends",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )

    # sideshow_order.created
    op.add_column(
        "sideshow_order",
        sa.Column("created_old", sa.DateTime(timezone=True), nullable=True),
    )
    sideshow_order = sa.sql.table(
        "sideshow_order",
        sa.sql.column("uuid"),
        sa.sql.column("created"),
        sa.sql.column("created_old"),
    )
    cursor = op.get_bind().execute(sideshow_order.select())
    for row in cursor.fetchall():
        op.get_bind().execute(
            sideshow_order.update()
            .where(sideshow_order.c.uuid == row.uuid)
            .values({"created_old": row.created})
        )
    op.drop_column("sideshow_order", "created")
    op.alter_column(
        "sideshow_order",
        "created_old",
        new_column_name="created",
        nullable=False,
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )

    # sideshow_customer_pending.created
    op.add_column(
        "sideshow_customer_pending",
        sa.Column("created_old", sa.DateTime(timezone=True), nullable=True),
    )
    sideshow_customer_pending = sa.sql.table(
        "sideshow_customer_pending",
        sa.sql.column("uuid"),
        sa.sql.column("created"),
        sa.sql.column("created_old"),
    )
    cursor = op.get_bind().execute(sideshow_customer_pending.select())
    for row in cursor.fetchall():
        op.get_bind().execute(
            sideshow_customer_pending.update()
            .where(sideshow_customer_pending.c.uuid == row.uuid)
            .values({"created_old": row.created})
        )
    op.drop_column("sideshow_customer_pending", "created")
    op.alter_column(
        "sideshow_customer_pending",
        "created_old",
        new_column_name="created",
        nullable=False,
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )

    # sideshow_batch_neworder_row.sale_ends
    op.add_column(
        "sideshow_batch_neworder_row",
        sa.Column("sale_ends_old", sa.DateTime(timezone=True), nullable=True),
    )
    sideshow_batch_neworder_row = sa.sql.table(
        "sideshow_batch_neworder_row",
        sa.sql.column("uuid"),
        sa.sql.column("sale_ends"),
        sa.sql.column("sale_ends_old"),
    )
    cursor = op.get_bind().execute(sideshow_batch_neworder_row.select())
    for row in cursor.fetchall():
        if row.sale_ends:
            op.get_bind().execute(
                sideshow_batch_neworder_row.update()
                .where(sideshow_batch_neworder_row.c.uuid == row.uuid)
                .values({"sale_ends_old": row.sale_ends})
            )
    op.drop_column("sideshow_batch_neworder_row", "sale_ends")
    op.alter_column(
        "sideshow_batch_neworder_row",
        "sale_ends_old",
        new_column_name="sale_ends",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )

    # sideshow_batch_neworder_row.modified
    op.add_column(
        "sideshow_batch_neworder_row",
        sa.Column("modified_old", sa.DateTime(timezone=True), nullable=True),
    )
    sideshow_batch_neworder_row = sa.sql.table(
        "sideshow_batch_neworder_row",
        sa.sql.column("uuid"),
        sa.sql.column("modified"),
        sa.sql.column("modified_old"),
    )
    cursor = op.get_bind().execute(sideshow_batch_neworder_row.select())
    for row in cursor.fetchall():
        if row.modified:
            op.get_bind().execute(
                sideshow_batch_neworder_row.update()
                .where(sideshow_batch_neworder_row.c.uuid == row.uuid)
                .values({"modified_old": row.modified})
            )
    op.drop_column("sideshow_batch_neworder_row", "modified")
    op.alter_column(
        "sideshow_batch_neworder_row",
        "modified_old",
        new_column_name="modified",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )

    # sideshow_batch_neworder.executed
    op.add_column(
        "sideshow_batch_neworder",
        sa.Column("executed_old", sa.DateTime(timezone=True), nullable=True),
    )
    sideshow_batch_neworder = sa.sql.table(
        "sideshow_batch_neworder",
        sa.sql.column("uuid"),
        sa.sql.column("executed"),
        sa.sql.column("executed_old"),
    )
    cursor = op.get_bind().execute(sideshow_batch_neworder.select())
    for row in cursor.fetchall():
        if row.executed:
            op.get_bind().execute(
                sideshow_batch_neworder.update()
                .where(sideshow_batch_neworder.c.uuid == row.uuid)
                .values({"executed_old": row.executed})
            )
    op.drop_column("sideshow_batch_neworder", "executed")
    op.alter_column(
        "sideshow_batch_neworder",
        "executed_old",
        new_column_name="executed",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )

    # sideshow_batch_neworder.created
    op.add_column(
        "sideshow_batch_neworder",
        sa.Column("created_old", sa.DateTime(timezone=True), nullable=True),
    )
    sideshow_batch_neworder = sa.sql.table(
        "sideshow_batch_neworder",
        sa.sql.column("uuid"),
        sa.sql.column("created"),
        sa.sql.column("created_old"),
    )
    cursor = op.get_bind().execute(sideshow_batch_neworder.select())
    for row in cursor.fetchall():
        op.get_bind().execute(
            sideshow_batch_neworder.update()
            .where(sideshow_batch_neworder.c.uuid == row.uuid)
            .values({"created_old": row.created})
        )
    op.drop_column("sideshow_batch_neworder", "created")
    op.alter_column(
        "sideshow_batch_neworder",
        "created_old",
        new_column_name="created",
        nullable=False,
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
    )
