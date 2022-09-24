# External Dataset Download Specification

## Table of Content
- [External Dataset Download Specification](#external-dataset-download-specification)
  - [Table of Content](#table-of-content)
  - [General Specification](#general-specification)
  - [Directories](#directories)
  - [Code Running Instructions](#code-running-instructions)


## General Specification
This process aims to download all external dataset, including:
- Including: 
  - property_and_elector
  - PTV = train station
  - hospital
  - emergency_service
  - public_service
  - care_facility
  - Income
  - population_growth
  - criminal
  - shopping center
  - school
## Directories

```

|-- data                              
		|-- curated                        
		        |-- external-data          
		|-- raw   
		        |-- external-data
        |-- external-raw-data
|-- notebookes  
        |-- external-data-download
                |-- download.ipynb                                               
|-- scripts                                   
        |-- external-data-download
                |-- download.py
                |-- utilis.py
```

## Code Running Instructions
1. Download Data
    - `download.ipynb`