from . import api
from .api import Craft
from .craftpopup import CraftScreen
from textual.widgets import DataTable

class DBColumn():
    def __init__(self, valuename: str, colname: str):
        self.valuename = valuename
        self.colname = colname

class ItemTable(DataTable):
    def __init__(self):
        super().__init__(
            cursor_type = "row",
            classes = "inventorytable"
        )

        self.invcolumns = [
            DBColumn("name", "Item Name"),
            DBColumn("size", "Amount in Inventory"),
            DBColumn("craftable", "Is Craftable")
        ]

        self.indexcol = "id"
        self.sortmethod = {
            "columns": ("name",), 
            "reverse": False
        }

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("n", "sort_name", "Sort by Name"),
        ("a", "sort_size", "Sort by Amount"),
        ("c", "sort_craftable", "Sort by Craftable")
    ]

    async def on_mount(self):
        await self.action_refresh()

    async def action_refresh(self):
        self.clear(columns=True)
        self.data = await api.get("/api/items/inv")

        for col in self.invcolumns:
            self.add_column(col.colname, key=col.valuename)
        
        for entry in self.data:
            row = []
            for col in self.invcolumns:
                cell = entry[col.valuename]
                if cell == False:
                    cell = ""
                elif cell == True:
                    cell = "Yes"
                row.append(cell)
            
            self.add_row(*row, key=entry[self.indexcol])
        
        self.sort(*self.sortmethod["columns"], reverse=self.sortmethod["reverse"])
    
    def action_sort_name(self):
        if self.sortmethod["columns"] == ("name",):
            self.sortmethod["reverse"] = not self.sortmethod["reverse"]
        
        self.sortmethod["columns"] = ("name",)
        self.sort(*self.sortmethod["columns"], reverse=self.sortmethod["reverse"])
    
    def action_sort_size(self):
        if self.sortmethod["columns"] == ("size", "name"):
            self.sortmethod["reverse"] = not self.sortmethod["reverse"]
        
        self.sortmethod["columns"] = ("size", "name")
        self.sort(*self.sortmethod["columns"], reverse=self.sortmethod["reverse"])
    
    def action_sort_craftable(self):
        if self.sortmethod["columns"] == ("craftable", "name"):
            self.sortmethod["reverse"] = not self.sortmethod["reverse"]
        
        self.sortmethod["columns"] = ("craftable", "name")
        self.sort(*self.sortmethod["columns"], reverse=self.sortmethod["reverse"])
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        for row in self.data:
            if row["id"] == event.row_key:
                selectedrow = row
                break

        if selectedrow["craftable"] == True:
            craft = Craft(type="item", id=selectedrow["id"])
            self.app.push_screen(CraftScreen(craft=craft))

class FluidTable(DataTable):
    def __init__(self):
        super().__init__(
            cursor_type = "row",
            classes = "inventorytable"
        )

        self.invcolumns = [
            DBColumn("name", "Fluid Name"),
            DBColumn("amount", "Amount in Inventory (ML)"),
            DBColumn("craftable", "Is Craftable")
        ]

        self.indexcol = "id"
        self.sortmethod = {
            "columns": ("name",), 
            "reverse": False
        }

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("n", "sort_name", "Sort by Name"),
        ("a", "sort_amount", "Sort by Amount"),
        ("c", "sort_craftable", "Sort by Craftable")
    ]

    async def on_mount(self):
        await self.action_refresh()

    async def action_refresh(self):
        self.clear(columns=True)
        self.data = await api.get("/api/fluids/inv")

        for col in self.invcolumns:
            self.add_column(col.colname, key=col.valuename)
        
        for entry in self.data:
            row = []
            for col in self.invcolumns:
                cell = entry[col.valuename]
                if cell == False:
                    cell = ""
                elif cell == True:
                    cell = "Yes"
                elif isinstance(cell, int):
                    cell = round(cell / 1000000, 2)
                    cell = str(cell) + " ML"
                row.append(cell)
            
            self.add_row(*row, key=entry[self.indexcol])
        
        self.sort(*self.sortmethod["columns"], reverse=self.sortmethod["reverse"])
    
    def action_sort_name(self):
        if self.sortmethod["columns"] == ("name",):
            self.sortmethod["reverse"] = not self.sortmethod["reverse"]
        
        self.sortmethod["columns"] = ("name",)
        self.sort(*self.sortmethod["columns"], reverse=self.sortmethod["reverse"])
    
    def action_sort_amount(self):
        if self.sortmethod["columns"] == ("amount", "name"):
            self.sortmethod["reverse"] = not self.sortmethod["reverse"]
        
        self.sortmethod["columns"] = ("amount", "name")
        self.sort(*self.sortmethod["columns"], reverse=self.sortmethod["reverse"])
    
    def action_sort_craftable(self):
        if self.sortmethod["columns"] == ("craftable", "name"):
            self.sortmethod["reverse"] = not self.sortmethod["reverse"]
        
        self.sortmethod["columns"] = ("craftable", "name")
        self.sort(*self.sortmethod["columns"], reverse=self.sortmethod["reverse"])
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        for row in self.data:
            if row["id"] == event.row_key:
                selectedrow = row
                break

        if selectedrow["craftable"] == True:
            craft = Craft(type="fluid", id=selectedrow["id"])
            self.app.push_screen(CraftScreen(craft=craft))

class EssentiaTable(DataTable):
    def __init__(self):
        super().__init__(
            cursor_type = "row",
            classes = "inventorytable"
        )

        self.invcolumns = [
            DBColumn("name", "Essentia Name"),
            DBColumn("amount", "Amount in Inventory")
        ]

        self.indexcol = "id"
        self.sortmethod = {
            "columns": ("name",), 
            "reverse": False
        }

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("n", "sort_name", "Sort by Name"),
        ("a", "sort_amount", "Sort by Amount")
    ]

    async def on_mount(self):
        await self.action_refresh()

    async def action_refresh(self):
        self.clear(columns=True)
        self.data = await api.get("/api/essentia/inv")

        for col in self.invcolumns:
            self.add_column(col.colname, key=col.valuename)
        
        for entry in self.data:
            row = []
            for col in self.invcolumns:
                cell = entry[col.valuename]
                if isinstance(cell, str):
                    cell = cell.split(" Super Critical Fluid")[0]
                row.append(cell)
            
            self.add_row(*row, key=entry[self.indexcol])
        
        self.sort(*self.sortmethod["columns"], reverse=self.sortmethod["reverse"])
    
    def action_sort_name(self):
        if self.sortmethod["columns"] == ("name",):
            self.sortmethod["reverse"] = not self.sortmethod["reverse"]
        
        self.sortmethod["columns"] = ("name",)
        self.sort(*self.sortmethod["columns"], reverse=self.sortmethod["reverse"])
    
    def action_sort_amount(self):
        if self.sortmethod["columns"] == ("amount", "name"):
            self.sortmethod["reverse"] = not self.sortmethod["reverse"]
        
        self.sortmethod["columns"] = ("amount", "name")
        self.sort(*self.sortmethod["columns"], reverse=self.sortmethod["reverse"])