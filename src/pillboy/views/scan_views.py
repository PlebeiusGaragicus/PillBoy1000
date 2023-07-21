import json
import re

from pillboy.gui.screens.screen import RET_CODE__BACK_BUTTON
from pillboy.models import DecodeQR, Seed
from pillboy.models.settings import SettingsConstants

from .view import BackStackView, MainMenuView, NotYetImplementedView, View, Destination



class ScanView(View):
    def run(self):
        from pillboy.gui.screens.scan_screens import ScanScreen

        wordlist_language_code = self.settings.get_value(SettingsConstants.SETTING__WORDLIST_LANGUAGE)
        self.decoder = DecodeQR(wordlist_language_code=wordlist_language_code)

        # Start the live preview and background QR reading
        ScanScreen(decoder=self.decoder).display()

        return Destination(MainMenuView)



class SettingsUpdatedView(View):
    def __init__(self, config_name: str):
        super().__init__()

        self.config_name = config_name
    

    def run(self):
        from pillboy.gui.screens.scan_screens import SettingsUpdatedScreen
        screen = SettingsUpdatedScreen(config_name=self.config_name)
        selected_menu_num = screen.display()

        if selected_menu_num == RET_CODE__BACK_BUTTON:
            return Destination(BackStackView)

        # Only one exit point
        return Destination(MainMenuView)

