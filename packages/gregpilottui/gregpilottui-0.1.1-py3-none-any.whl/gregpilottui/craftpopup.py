from textual.screen import ModalScreen
from textual.containers import Vertical
from textual.widgets import Input, Button, Label
from textual.events import Key, Click
from .api import Craft

class CraftScreen(ModalScreen):
    CSS_PATH = "gp.tcss"

    def __init__(self, *, craft: Craft):
        super().__init__()
        self.craft = craft
    
    def compose(self):
        yield CraftPopup(craft=self.craft)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "successbutton" or event.button.id == "failbutton":
            self.dismiss(True)
        
    def on_key(self, event: Key):
        if event.key == "escape":
            self.dismiss()
        
    def on_click(self, event: Click):
        if event.button == 3:
            self.dismiss()

class CraftSuccessButton(Button):
    def __init__(self):
        super().__init__("Craft submitted!", variant="success", id="successbutton", classes="craftbutton")

class CraftFailButton(Button):
    def __init__(self):
        super().__init__("Error: Craft not submitted.", variant="warning", id="failbutton", classes="craftbutton")

class CraftPopup(Input):
    def __init__(self, *, craft: Craft):
        super().__init__()
        self.craft = craft
        self.type = "integer"
        self.placeholder = "Enter amount to craft..."
    
    def on_mount(self):
        self.focus()

    async def on_input_submitted(self, event: Input.Submitted):
        self.craft.amount = int(event.value)
        success = self.craft.submit()

        if success:
            await self.app.screen.mount(
                CraftSuccessButton(),
                before=None,
            )
        else:
            await self.app.screen.mount(
                CraftFailButton(),
                before=None
            )

        self.remove()