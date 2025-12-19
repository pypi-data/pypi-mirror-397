import os
import yaml
from typing import List


def get_places() -> List:
    """
    Load the places.yaml file and return the list of common places in the system.
    """

    home_dir = os.environ.get("HOME")
    places_file = os.path.join(home_dir, ".config", "gremux", "places.yaml")

    if not os.path.exists(places_file):
        return None

    with open(places_file) as fh:
        places = yaml.safe_load(fh)

    return places["places"]
