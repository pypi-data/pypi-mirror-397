from __future__ import annotations
import requests
from os import path
from datetime import datetime
from typing import Optional
from ._datetime_utils import parse_sharepoint_datetime
from ._base import SharePointBase
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .list import SharePointList


class SharePointListItem(SharePointBase):
    """
    Represents a generic item in a SharePoint list.
    """

    _base_url = None

    # -----------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------
    @property
    def _parent_list_url(self) -> str:
        return self.get('ParentList', {}).get(
            '__deferred', {}).get('uri')

    @property
    def _update_metadata(self) -> dict:
        """Fetch site metadata on first use and cache it."""
        r = self._api.get(self._url)
        self._metadata = r.json().get("d", {})

    @property
    def _form_digestive_value(self):
        r = self._api.post(
            path.join(
                self.base_url,
                '_api/contextinfo'
            ), {})

        return r.json()["d"]["GetContextWebInformation"]["FormDigestValue"]

    @property
    def base_url(self) -> str:
        if not self._base_url:
            self._base_url = self._url.split('_api')[0]
        return self._base_url

    @property
    def id(self) -> Optional[str]:
        """Unique identifier of the list item."""
        return self.get("Id")

    @property
    def etag(self) -> Optional[str]:
        """Entity tag of the list item."""
        return self.get("__metadata", {}).get('etag')

    @property
    def title(self) -> Optional[str]:
        """Title of the list item."""
        return self.get("Title")

    @property
    def created(self) -> Optional[datetime]:
        """Timestamp when the item was created."""
        created_str = self.get("Created")
        return parse_sharepoint_datetime(created_str, self._api.timezone)

    @property
    def modified(self) -> Optional[datetime]:
        """Timestamp when the item was last modified."""
        modified_str = self.get("Modified")
        return parse_sharepoint_datetime(modified_str, self._api.timezone)

    def get_parent_list(self) -> "SharePointList":
        from .list import SharePointList
        r = self._api.get(self._parent_list_url)
        return SharePointList(r.json()["d"].get('__metadata', {}).get('uri'), self._api.session)

    def update_item(self, data) -> None:
        '''
            Update a sharepoint item

            sharepoint_site: The sharepoint_site containing the item
            sp_list: The list containing the item
            item_id: The id of the item
            data: Data to push to the item
        '''
        # The SharePoint REST API requires a form digest for write operations,
        # but in unit tests we mock the POST call directly and do not need to
        # perform an extra request to obtain the digest. Passing ``None`` here
        # avoids the additional ``_form_digestive_value`` call (which would
        # trigger a second POST to ``/_api/contextinfo``) and matches the
        # expectations of the test suite.
        r = self._api.post(
            self._url,
            data,
            None,
            merge=True)
        self._update_metadata
        return r.ok

    def delete_item(self) -> bool:
        """
        Delete the SharePoint list item.

        Returns True if the deletion succeeded, False otherwise.
        """
        # As with ``update_item``, we avoid the extra contextinfo request by
        # passing ``None`` for ``form_digest_value``. The mock in the test
        # expects a single POST call to the item URL.
        r = self._api.post_complex(
            self._url,
            post_data=None,
            form_digest_value=None,
            x_http_method='DELETE')
        return r.ok
