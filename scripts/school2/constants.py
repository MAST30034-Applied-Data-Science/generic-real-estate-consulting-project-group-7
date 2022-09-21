"""
Define constants
"""

import numpy as np

# REQUESTS HEADER
headers = {
    "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"
}

# DOMAIN HOME URL
home_url = {
    "domain": "https://www.domain.com.au",
    "realestate": "https://www.realestate.com.au",
}

# DOMAIN Property Selected columns
domain_property_attributes = [
    # "rentalMethod",
    # "address",
    # "suburb",
    # "price",
    # "bedrooms",
    # "bathrooms",
    # "parking",  # car park
    "postcode",
    # "state",
    # "primaryPropertyType",
    # "secondaryPropertyType",
    # "agency",
]

# VALID postcodes list
postcodes = {
    "NSW": np.concatenate(
        [
            np.arange(2000, 2600),
            np.arange(2619, 2900),
            np.arange(2921, 3000),
        ]
    ),
    "ACT": np.concatenate([np.arange(2600, 2619), np.arange(2900, 2921)]),
    "VIC": np.arange(3000, 4000),
    "QLD": np.arange(4000, 5000),
    "SA": np.arange(5000, 5800),
    "WA": np.arange(6000, 6798),
    "TAS": np.arange(7000, 7800),
    "NT": np.arange(800, 900),
}
