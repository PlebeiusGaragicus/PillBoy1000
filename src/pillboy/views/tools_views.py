import hashlib
import os

import time

from PIL import Image
from PIL.ImageOps import autocontrast
from pillboy.controller import Controller
from pillboy.gui.screens.screen import LoadingScreenThread, QRDisplayScreen

from pillboy.hardware.camera import Camera
from pillboy.gui.components import FontAwesomeIconConstants, GUIConstants, SeedSignerCustomIconConstants
from pillboy.gui.screens import (RET_CODE__BACK_BUTTON, ButtonListScreen)
from pillboy.models.encode_qr import EncodeQR
from pillboy.models.qr_type import QRType
from pillboy.models.settings_definition import SettingsConstants

from .view import View, Destination, BackStackView, NotYetImplementedView



class ToolsMenuView(View):
    def run(self):
        IMAGE = (" New seed", FontAwesomeIconConstants.CAMERA)
        DICE = ("New seed", FontAwesomeIconConstants.DICE)
        KEYBOARD = ("Calc 12th/24th word", FontAwesomeIconConstants.KEYBOARD)
        button_data = [IMAGE, DICE, KEYBOARD]
        screen = ButtonListScreen(
            title="Tools",
            is_button_text_centered=False,
            button_data=button_data
        )
        selected_menu_num = screen.display()

        if selected_menu_num == RET_CODE__BACK_BUTTON:
            return Destination(BackStackView)

        elif button_data[selected_menu_num] == IMAGE:
            return Destination(NotYetImplementedView)

        elif button_data[selected_menu_num] == DICE:
            return Destination(NotYetImplementedView)

        elif button_data[selected_menu_num] == KEYBOARD:
            return Destination(NotYetImplementedView)
