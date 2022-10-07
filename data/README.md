# Data Specification

## Table of Content
- [Data Specification](#data-specification)
  - [Table of Content](#table-of-content)
  - [Folder Specification](#folder-specification)


## Folder Specification
```
|-- data                                     # store raw and preprocessed data
	|-- curated                          # store processed data
                |-- domain-website-data      # store processed domain data
                |-- external-data            # store processed external features
                |-- model-data               # store model data
                |-- ors-data
	|-- external-raw-data                # store raw external datasets which cannot using url to download
	|-- raw                              # store raw external datasets 
                |-- domain-website-data      # store raw domain data
                |-- external-data            # store raw external features
                |-- model-data
                |-- ors-data                 # store raw ors datasets
```