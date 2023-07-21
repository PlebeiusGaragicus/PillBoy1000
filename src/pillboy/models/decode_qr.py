import base64
import json
import logging
import re

from binascii import a2b_base64, b2a_base64
from enum import IntEnum
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol


from . import QRType, Seed
from .settings import SettingsConstants


logger = logging.getLogger(__name__)



class DecodeQRStatus(IntEnum):
    """
        Used in DecodeQR to communicate status of adding qr frame/segment
    """
    PART_COMPLETE = 1
    PART_EXISTING = 2
    COMPLETE = 3
    FALSE = 4
    INVALID = 5




class BaseQrDecoder:
    def __init__(self):
        self.total_segments = None
        self.collected_segments = 0
        self.complete = False

    @property
    def is_complete(self) -> bool:
        return self.complete

    def add(self, segment, qr_type):
        raise Exception("Not implemented in child class")



class BaseSingleFrameQrDecoder(BaseQrDecoder):
    def __init__(self):
        super().__init__()
        self.total_segments = 1



class BaseAnimatedQrDecoder(BaseQrDecoder):
    def __init__(self):
        super().__init__()
        self.segments = []

    def current_segment_num(self, segment) -> int:
        raise Exception("Not implemented in child class")

    def total_segment_nums(self, segment) -> int:
        raise Exception("Not implemented in child class")

    def parse_segment(self, segment) -> str:
        raise Exception("Not implemented in child class")
    
    @property
    def is_valid(self) -> bool:
        return True

    def add(self, segment, qr_type=None):
        if self.total_segments == None:
            self.total_segments = self.total_segment_nums(segment)
            self.segments = [None] * self.total_segments
        elif self.total_segments != self.total_segment_nums(segment):
            raise Exception('Segment total changed unexpectedly')

        if self.segments[self.current_segment_num(segment) - 1] == None:
            self.segments[self.current_segment_num(segment) - 1] = self.parse_segment(segment)
            self.collected_segments += 1
            if self.total_segments == self.collected_segments:
                if self.is_valid:
                    self.complete = True
                    return DecodeQRStatus.COMPLETE
                else:
                    return DecodeQRStatus.INVALID
            return DecodeQRStatus.PART_COMPLETE # new segment added

        return DecodeQRStatus.PART_EXISTING # segment not added because it's already been added





# TODO: Refactor this to work with the new SettingsDefinition
class SettingsQrDecoder(BaseSingleFrameQrDecoder):
    def __init__(self):
        super().__init__()
        self.settings = {}
        self.config_name = None


    def add(self, segment, qr_type=QRType.SETTINGS):
        # print(f"SettingsQR:\n{segment}")
        try:
            self.settings = {}

            # QR Settings format is space-separated key/value pairs, but should also
            # parse \n-separated keys.
            for entry in segment.split():
                key = entry.split("=")[0].strip()
                value = entry.split("=")[1].strip()
                self.settings[key] = value

            # Remove values only needed for import
            self.settings.pop("type", None)
            version = self.settings.pop("version", None)
            if not version or int(version) != 1:
                raise Exception(f"Settings QR version {version} not supported")

            self.config_name = self.settings.pop("name", None)
            if self.config_name:
                self.config_name = self.config_name.replace("_", " ")
            
            # Have to translate the abbreviated settings into the human-readable values
            # used in the normal Settings.
            map_abbreviated_enable = {
                "0": SettingsConstants.OPTION__DISABLED,
                "1": SettingsConstants.OPTION__ENABLED,
                "2": SettingsConstants.OPTION__PROMPT,
            }
            map_abbreviated_sig_types = {
                "s": SettingsConstants.SINGLE_SIG,
                "m": SettingsConstants.MULTISIG,
            }
            map_abbreviated_scripts = {
                "na": SettingsConstants.NATIVE_SEGWIT,
                "ne": SettingsConstants.NESTED_SEGWIT,
                "tr": SettingsConstants.TAPROOT,
                "cu": SettingsConstants.CUSTOM_DERIVATION,
            }
            map_abbreviated_coordinators = {
                "bw": SettingsConstants.COORDINATOR__BLUE_WALLET,
                "sw": SettingsConstants.COORDINATOR__SPARROW,
                "sd": SettingsConstants.COORDINATOR__SPECTER_DESKTOP,
            }

            def convert_abbreviated_value(category, key, abbreviation_map, is_list=False, new_key_name=None):
                try:
                    if key not in self.settings:
                        print(f"'{key}' not found in settings")
                        return
                    value = self.settings[key]

                    if not is_list:
                        new_value = abbreviation_map.get(value)
                        if not new_value:
                            logger.error(f"No abbreviation map value for \"{value}\" for setting {key}")
                            return
                    else:
                        # `value` is a comma-separated list; yields list of map matches
                        values = value.split(",")
                        new_value = []
                        for v in values:
                            mapped_value = abbreviation_map.get(v)
                            if not mapped_value:
                                logger.error(f"No abbreviation map value for \"{v}\" for setting {key}")
                                return
                            new_value.append(mapped_value)
                    del self.settings[key]
                    if new_key_name:
                        key = new_key_name
                    if category not in self.settings:
                        self.settings[category] = {}
                    self.settings[category][key] = new_value
                except Exception as e:
                    logger.exception(e)
                    return

            convert_abbreviated_value("wallet", "coord", map_abbreviated_coordinators, is_list=True, new_key_name="coordinators")
            convert_abbreviated_value("features", "xpub", map_abbreviated_enable, new_key_name="xpub_export")
            convert_abbreviated_value("features", "sigs", map_abbreviated_sig_types, is_list=True, new_key_name="sig_types")
            convert_abbreviated_value("features", "scripts", map_abbreviated_scripts, is_list=True, new_key_name="script_types")
            convert_abbreviated_value("features", "xp_det", map_abbreviated_enable, new_key_name="show_xpub_details")
            convert_abbreviated_value("features", "passphrase", map_abbreviated_enable)
            convert_abbreviated_value("features", "priv_warn", map_abbreviated_enable, new_key_name="show_privacy_warnings")
            convert_abbreviated_value("features", "dire_warn", map_abbreviated_enable, new_key_name="show_dire_warnings")

            self.complete = True
            self.collected_segments = 1
            return DecodeQRStatus.COMPLETE
        except Exception as e:
            logger.exception(e)
            return DecodeQRStatus.INVALID
