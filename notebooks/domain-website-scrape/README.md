# Domain Website Scrape Specification

## Table of Content
- [Domain Website Scrape Specification](#domain-website-scrape-specification)
  - [Table of Content](#table-of-content)
  - [General Specification](#general-specification)
  - [Directories](#directories)
  - [Code Running Instructions](#code-running-instructions)
  - [Visualization](#visualization)


## General Specification
This process aims to find house rental data from [domain]('https://www.domain.com.au/') website.
## Directories

```

|-- data                              
		|-- curated                        
		        |-- domain-website-data          
		|--raw   
		        |-- domain-website-data   
|-- duprecated
        |-- domain-website-scrape
|-- notebookes  
        |-- domain-website-scrape
                |-- download.ipynb
                |-- domain-data-visualization.twb           
|-- plots              
        |-- domain-website-scrape
                |-- domain-website-visualization.png                                                
|-- scripts                                   
        |-- domain-website-scrape
                |-- download.py
                |-- scrape_domain.py
                |-- utilis.py
                |-- constants.py
```

## Code Running Instructions
1. Download Data
    - `download.ipynb`

## Visualization
1. Visualization focus on different postocode

![Drag Racing](../plots/../../plots/domain-website-scrape/domain-website-visualization.png)