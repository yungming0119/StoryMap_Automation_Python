from arcgis.gis import GIS


class PortalItemLookupError(RuntimeError):
    """Raised when a county StoryMap item cannot be retrieved."""


class portal_items:
    def __init__(self, gis=None, username=None, county=None):
        self.gis = gis or GIS("home")
        self.username = username or self.gis.users.me.username
        self.user = self.gis.users.get(self.username)
        self.folder_name = f"{county} County"
        self.items = self.get_name_id_dict(self.folder_name)

    def get_items_in_folder(self, folder_name):
        """
        Returns all items inside a specific folder.
        """
        return self.user.items(folder=folder_name)

    def get_name_id_dict(self, folder_name):
        """
        Returns a dictionary mapping item titles → item IDs for a folder.
        """
        try:
            items = self.get_items_in_folder(folder_name)
        except Exception as exc:
            raise PortalItemLookupError(
                f"Unable to retrieve StoryMap items from portal folder "
                f"'{folder_name}'."
            ) from exc
        return {item.title: item.itemid for item in items}

    def get_name_id_type_dict(self, folder_name):
        """
        Returns a dictionary mapping item titles → {id, type}.
        """
        items = self.get_items_in_folder(folder_name)
        return {
            item.title: {
                "id": item.itemid,
                "type": item.type
            }
            for item in items
        }
    
    def __getitem__(self, key):
        try:
            return self.items[key]
        except KeyError as exc:
            available_items = ", ".join(sorted(self.items)) or "none"
            raise PortalItemLookupError(
                f"StoryMap item '{key}' was not found in portal folder "
                f"'{self.folder_name}'. Available items: {available_items}."
            ) from exc
