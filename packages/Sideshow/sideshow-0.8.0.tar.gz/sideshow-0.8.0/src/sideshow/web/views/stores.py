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
Views for Stores
"""

from wuttaweb.views import MasterView

from sideshow.db.model import Store


class StoreView(MasterView):  # pylint: disable=abstract-method
    """
    Master view for
    :class:`~sideshow.db.model.stores.Store`; route prefix
    is ``stores``.

    Notable URLs provided by this class:

    * ``/stores/``
    * ``/stores/new``
    * ``/stores/XXX``
    * ``/stores/XXX/edit``
    * ``/stores/XXX/delete``
    """

    model_class = Store

    labels = {
        "store_id": "Store ID",
    }

    filter_defaults = {
        "archived": {"active": True, "verb": "is_false"},
    }

    sort_defaults = "store_id"

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)

        # links
        g.set_link("store_id")
        g.set_link("name")

    def grid_row_class(  # pylint: disable=unused-argument,empty-docstring
        self, store, data, i
    ):
        """ """
        if store.archived:
            return "has-background-warning"
        return None

    def configure_form(self, form):  # pylint: disable=empty-docstring
        """ """
        f = form
        super().configure_form(f)

        # store_id
        f.set_validator("store_id", self.unique_store_id)

        # name
        f.set_validator("name", self.unique_name)

    def unique_store_id(self, node, value):  # pylint: disable=empty-docstring
        """ """
        model = self.app.model
        session = self.Session()

        query = session.query(model.Store).filter(model.Store.store_id == value)

        if self.editing:
            uuid = self.request.matchdict["uuid"]
            query = query.filter(model.Store.uuid != uuid)

        if query.count():
            node.raise_invalid("Store ID must be unique")

    def unique_name(self, node, value):  # pylint: disable=empty-docstring
        """ """
        model = self.app.model
        session = self.Session()

        query = session.query(model.Store).filter(model.Store.name == value)

        if self.editing:
            uuid = self.request.matchdict["uuid"]
            query = query.filter(model.Store.uuid != uuid)

        if query.count():
            node.raise_invalid("Name must be unique")


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    base = globals()

    StoreView = kwargs.get(  # pylint: disable=redefined-outer-name,invalid-name
        "StoreView", base["StoreView"]
    )
    StoreView.defaults(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
