# Generic Real Estate Consulting Project

# Table of contents
- [Generic Real Estate Consulting Project](#generic-real-estate-consulting-project)
- [Table of contents](#table-of-contents)
  - [Project Specification:](#project-specification)
  - [Group Information](#group-information)
  - [Dependencies](#dependencies)
  - [Directories](#directories)

## Project Specification:

Due to the impact of covid, uncertain factors such as insufficient human resources and decreased purchasing power accelerate the instability in the property market.This project utilizes modern data science analysis tools, and aims to help the real-estate industry in making investment and client-based marketing to achieve higher profit.

**Our main goal is to determine the approximate level of rent and which properties are most likely to increase in the next 3 years.**

This whole project took 7 weeks, about 150 hours to complete including the final wrap up session.

## Group Information
**Group name:** Group 7
    
| Student Name | Student ID | Email |
| ---- | ---- | ---- |
| QUZIHAN WU | 1078419 | quzihanw@student.unimelb.edu.au |
| YINAN LI | 1173947 | yinan3@student.unimelb.edu.au | 
| XINGYAO WANG | 1179108 |xingyaow@student.unimelb.edu.au  |
| ZIXUAN GUO | 1124606 |mollyguo123123@gmail.com  |
| ZONGCHAO XIE | 1174047 |zongchaox@student.unimelb.edu.au  |

## Dependencies
**[MANDATORY]**

The project is conducted with `python` environment, please install required dependencies before executing any notebooks.
```bash
# install dependencies
pip install -r requirements.txt
```

## Directories
    
- `data`: store required datasets
    - `curated`: store processed datasets
    - `external-raw-data`: store raw datasets which directly pushed
    - `raw`: store raw datastes
- `models`: modelling
    - `Question 1.ipynb`: What are the most important internal and external features in predicting rental prices?
    - `Question 2.ipynb`:What are the top 10 suburbs with the highest predicted growth rate?
    - `Question 3.ipynb`: What are the most liveable and affordable suburbs according to your chosen metrics?
- `notebooks`: store data pipeline code
    - `domain-website-scrape`: domain website data
    - `external-data-download`: all external dataset
    - `preprocessing`: internal and external features preprocessing
    - `visualization`: visualization
- `plots`: store processed plot
- `scripts`: store data pipeline code
    - `domain-website-scrape`: domain website data .py file
    - `external-data-download`: all external dataset .py file
    - `preprocessing`: internal and external features preprocessing .py file
- `weekly-meeting-notes`: store weekly meeting minutes
- `Presentation`: store presentation slides
