"""
Define constants
"""

import numpy as np

# REQUESTS HEADER
user_agents = [
    "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    "Opera/9.25 (Windows NT 5.1; U; en)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)",
    "Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
]

proxies = {"http": "http://139.99.237.62:80", "https": "https://103.1.184.238:3128"}

# DOMAIN HOME URL
home_url = {
    "domain": "https://www.domain.com.au",
    "realestate": "https://www.realestate.com.au",
}

# DOMAIN Property Selected columns
domain_property_attributes = [
    "rentalMethod",
    "address",
    "suburb",
    "price",
    "beds",
    "baths",
    "parking",  # car park
    "postcode",
    "state",
    "primaryPropertyType",
    "secondaryPropertyType",
    "agency",
]

# DOMAIN property feature list
domain_property_features = [
    "beds",
    "baths",
    "parking",
    "propertyType",
    "propertyTypeFormatted",
    "isRural",
    "landSize",
    "landUnit",
    "isRetirement",
]

# DOMAIN property schemas
domain_property_schemas = {
    "property_id": int,
    "street": str,
    "suburb": str,
    "postcode": int,
    "latitude": float,
    "longitude": float,
    "price": str,
    "bedrooms": int,
    "bathrooms": int,
    "parking": int,
    "property_type": str,
    "land_size": int,
    "land_unit": str,
    "is_rural": bool,
    "is_retirement": bool,
    "url": str,
}

# Domain property selected columns
domain_property_columns = [
    "property_id",
    "street",
    "suburb",
    "state",
    "postcode",
    "latitude",
    "longitude",
    "price",
    "bedrooms",
    "bathrooms",
    "parking",
    "property_type",
    "is_rural",
    "land_size",
    "land_unit",
    "is_retirement",
    "url",
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
    "VIC_SAMPLE": np.arange(3900,3910),
    "QLD": np.arange(4000, 5000),
    "SA": np.arange(5000, 5800),
    "WA": np.arange(6000, 6798),
    "TAS": np.arange(7000, 7800),
    "NT": np.arange(800, 900),
}
