import requests
from textual import work
from textual.screen import ModalScreen
from textual.containers import Center
from textual.widgets import Input, Button, Label
from textual.events import Key, Click
from .api import Craft

class InitialConfigScreen(ModalScreen[str]):
    CSS_PATH = "gp.tcss"

    def __init__(self):
        super().__init__()
        self.id = "initscreen"
    
    def compose(self):
        yield Center(
            Label("Enter server URL (e.g, https://gregpilot.host.tld or http://192.168.10.10:4734):"),
            InitPopup()
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "successbutton":
            self.dismiss(self.url)
        elif event.button.id == "failbutton":
            self.app.exit()

class InitSuccessButton(Button):
    def __init__(self):
        super().__init__("Config Saved!", variant="success", id="successbutton", classes="initbutton")

class InitFailButton(Button):
    def __init__(self):
        super().__init__("Error: Config not saved.", variant="warning", id="failbutton", classes="initbutton")

class InitPopup(Input):
    def __init__(self):
        super().__init__()
        self.placeholder = "Server URL"
    
    def on_mount(self):
        self.focus()

    async def ping(self):
        tryurl = self.screen.url + "/api/power"
        try:
            response = requests.get(tryurl)
            if response.json()["powerstored"]:
                return True
            else:
                return False
        except:
            return False

    async def on_input_submitted(self, event: Input.Submitted):
        scr = self.screen
        scr.url = event.value
        success = await self.ping()

        if success == True:
            await scr.mount(
                Center(InitSuccessButton()),
                before=None,
            )
        else:
            await scr.mount(
                Center(InitFailButton()),
                before=None
            )

        self.remove()