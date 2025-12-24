from typing import Literal, List
from pathlib import Path
import json
from .savefile import SaveFile, HexColor, GenericCountry, COUNTRIES, TERRITORIES, GENERIC_COUNTRIES, PageType
import logging
from copy import deepcopy

logger = logging.getLogger("mapchart")


class Save:

    def __init__(self, save_file: Path | None = None) -> None:
        """
        Creates a new instance of the Save class
        
        :param self: Description
        :param save_file: An optional already existing save file
        :type save_file: Path | None
        """
        self.data: SaveFile

        if save_file:
            with save_file.open("r", encoding="UTF-8") as f:
                self.data = json.load(f)

            save_annotations = SaveFile.__annotations__
            if not self.data:
                raise ValueError("Failed to load save data!")

            self.data["zoomLevel"] = float(self.data["zoomLevel"])
            self.data["zoomX"] = float(self.data["zoomX"])
            self.data["zoomY"] = float(self.data["zoomY"])

            for key, value in self.data.items():
                if key not in save_annotations:
                    logger.warning(f"Key {key} does not exist in map type!")

                if type(value) != save_annotations.get(key):
                    logger.warning(
                        f"Key {key} type doesn't match expectations ({type(value)} is not {(save_annotations.get(key))})"
                    )
        else:
            self.data = {
                "groups": {},
                "title": "",
                "hidden": list(COUNTRIES + TERRITORIES),
                "background": "#FFFFFF",
                "borders": "#000",
                "legendFont": "Century Gothic",
                "legendFontColor": "#000",
                "legendBorderColor": "#00000000",
                "legendBgColor": "#00000000",
                "legendWidth": 150,
                "legendBoxShape": "square",
                "areBordersShown": True,
                "defaultColor": "#d1dbdd",
                "labelsColor": "#6a0707",
                "labelsFont": "Arial",
                "strokeWidth": "medium",
                "areLabelsShown": False,
                "uncoloredScriptColor": "#ffff33",
                "zoomLevel": 1.00,
                "zoomX": 0.00,
                "zoomY": 0.00,
                "v6": True,
                "page": "world",
                "usaStatesShown": False,
                "canadaStatesShown": False,
                "splitUK": False,
                "legendPosition": "bottom_left",
                "legendSize": "medium",
                "legendTranslateX": 0.00,
                "legendStatus": "show",
                "scalingPatterns": True,
                "legendRowsSameColor": True,
                "legendColumnCount": 1
            }

    def fill_country(self,
                     country: GenericCountry,
                     color: HexColor,
                     label: str = "") -> None:
        """
        Fills in a country with a certain colour
        
        :param self: Instance of the Save class
        :param country: Which country to fill
        :type country: GenericCountry
        :param color: Which colour to paint it as (use Hex, aka #ffffff)
        :type color: HexColor
        :param label: An optional label for the color
        :type label: str
        """
        self.clear_country(country)

        color = color.lower()

        logger.info(f"Filling in country {country} with {color}")
        if color not in self.data["groups"]:
            logger.info(f"Creating new color group for {color}")

            self.data["groups"][color] = {"label": label, "paths": [country]}
        else:
            self.data["groups"][color]["paths"].append(country)

        try:
            self.data["hidden"].remove(country)
        except ValueError:
            pass

    def create_group(self,
                     color: HexColor,
                     label: str = "",
                     override_existing: bool = False) -> None:
        """
        Creates a color group
        
        :param self: An instance of the Save calss
        :param color: The hex color of the group
        :type color: HexColor
        :param label: Label of the group (optional, uses an empty string by default)
        :type label: str
        :param override_existing: Whether to override an existing group if one exists (optional, False by default)
        :type override_existing: bool
        :raises ValueError: if color already exists and override_existing is set to False (or not specified)
        """

        if color in self.data["groups"] and not override_existing:
            raise ValueError("Group already exists!")

        self.data["groups"][color.lower()] = {"label": label, "paths": []}

    def set_map_type(self, map_type: PageType):
        """
        Changes the map type (e.g Europe, World, etc..)
        
        :param self: Instance of the Save class
        :param map_type: Type of the map (E.g Europe, Asia...)
        :type map_type: PageType
        """
        self.data["page"] = map_type

    @staticmethod
    def get_area_type(area: str) -> Literal["country", "territory"] | None:
        """
        Returns whether an area is a country, territory, or neither.
        If the area is a country, the function returns "country"
        If the area is a territory, the function returns "territory"
        If the area is neither, the function returns None
        
        :param area: Name of the territory. **This is case sensitive**.
        :type area: str
        :return: Area type (e.g "country", "territory", or None)
        :rtype: Literal['country', 'territory'] | None
        """
        if area in COUNTRIES:
            return "country"

        if area in TERRITORIES:
            return "territory"

        return None

    @staticmethod
    def get_countries_and_territories() -> List[GenericCountry]:
        """
        Returns a list of countries and territories supported by mapchart
        
        :return: List of countries and territories
        :rtype: List[GenericCountry]
        """
        return list(COUNTRIES + TERRITORIES)

    @staticmethod
    def format_country(country: str) -> GenericCountry | None:
        """
        Tries turning a country name into a format accepted by mapchart. (E.g: French guiana -> French_Guiana)
        
        :param country: possible country or territory thats name is going to be converted
        :type country: str
        :return: Formatted string if country exists, None if it doesn't
        :rtype: Area | None
        """
        if country in GENERIC_COUNTRIES:
            return country

        adapted_country: str = "_".join([
            country.capitalize()
            for country in country.lower().replace("-", " ").split(" ")
        ])
        print(adapted_country)
        if adapted_country in GENERIC_COUNTRIES:
            return adapted_country

        return None

    def clear_country(self, country: GenericCountry) -> bool:
        """
        Clears a certain country of its colour
        
        :param self: Instance of the save class
        :param country: The country to have its color removed
        :type country: GenericCountry
        :return: Whether the country was removed successfully
        :rtype: bool
        """
        removed: bool = False

        for color in deepcopy(self.data["groups"]):
            try:
                self.data["groups"][color]["paths"].remove(country)
                removed = True
            except ValueError:
                pass

        return removed

    def get_file(self) -> dict:
        """
        Returns the contents of a new Mapchart JSON file.
        
        :param self: Instance of the Save class
        :return: JSON string of the new Mapchart map
        :rtype: dict[Any, Any]
        """
        d = dict(self.data)
        self.data["zoomLevel"] = float(self.data["zoomLevel"])
        self.data["zoomX"] = float(self.data["zoomX"])
        self.data["zoomY"] = float(self.data["zoomY"])

        return d
