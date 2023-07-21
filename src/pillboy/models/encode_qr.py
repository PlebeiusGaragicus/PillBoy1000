import math

from binascii import b2a_base64, hexlify
from dataclasses import dataclass
from typing import List
from pillboy.helpers.qr import QR
from pillboy.models import Seed, QRType

from pillboy.models.settings import SettingsConstants



@dataclass
class EncodeQR:
    """
       Encode psbt for displaying as qr image
    """
    # TODO: Refactor so that this is a base class with implementation classes for each
    # QR type. No reason exterior code can't directly instantiate the encoder it needs.

    # Dataclass input vars on __init__()
    passphrase: str = None
    derivation: str = None
    network: str = SettingsConstants.MAINNET
    qr_type: str = None
    qr_density: str = SettingsConstants.DENSITY__MEDIUM
    wordlist_language_code: str = SettingsConstants.WORDLIST_LANGUAGE__ENGLISH
    bitcoin_address: str = None

    def __post_init__(self):
        self.qr = QR()

        if not self.qr_type:
            raise Exception('qr_type is required')

        if self.qr_density == None:
            self.qr_density = SettingsConstants.DENSITY__MEDIUM

        self.encoder: BaseQrEncoder = None

        ### CODE REMOVED


    def total_parts(self) -> int:
        return self.encoder.seq_len()


    def next_part(self):
        return self.encoder.next_part()


    def part_to_image(self, part, width=240, height=240, border=3):
        return self.qr.qrimage_io(part, width, height, border)


    def next_part_image(self, width=240, height=240, border=3, background_color="bdbdbd"):
        part = self.next_part()
        if self.qr_type == QRType.SEED__SEEDQR:
            return self.qr.qrimage(part, width, height, border)
        else:
            return self.qr.qrimage_io(part, width, height, border, background_color=background_color)


    # TODO: Make these properties?
    def is_complete(self):
        return self.encoder.is_complete


    def get_qr_density(self):
        return self.qr_density


    def get_qr_type(self):
        return self.qr_type



class BaseQrEncoder:
    def seq_len(self):
        raise Exception("Not implemented in child class")

    def next_part(self) -> str:
        raise Exception("Not implemented in child class")

    @property
    def is_complete(self):
        raise Exception("Not implemented in child class")

    def _create_parts(self):
        raise Exception("Not implemented in child class")
