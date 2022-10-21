# Generic Real Estate Consulting Project

# Table of contents
- [Generic Real Estate Consulting Project](#generic-real-estate-consulting-project)
- [Table of contents](#table-of-contents)
  - [Project Specification:](#project-specification)
  - [Group Information](#group-information)
  - [Dependencies](#dependencies)
  - [Directories](#directories)
  - [Clone](#clone)
  - [References](#references)

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
| ZIXUAN GUO | 1124606 |zixguo@student.unimelb.edu.au  |
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
      - will print out 3 years prediction here
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


## Clone
```bash
# install HomeBrew
# install lfs
brew install git-lfs
# run
git lfs install
git lfs clone #repository
```
## References
- NGUYEN, J. (2021). 4 Key Factors That Drive the Real Estate Market. investopedia. https://www.investopedia.com/articles/mortages-real-estate/11/factors-affecting-real-estate-market.asp
- Gomez, J. (2022). 8 critical factors that influence a home’s value. Opendoor. https://www.opendoor.com/w/blog/factors-that-influence-home-value
- Carbines, S. (2018). Victoria’s most expensive rental suburbs. realestate.com.au. https://www.realestate.com.au/news/victorias-most-expensive-rental-suburbs/
- (n.d.). Top Primary Schools in VIC. Cluey Learning. https://clueylearning.com.au/en/school-rankings/top-primary-schools/vic/
- (2021). Best Schools, Ranked by Median VCE Score, Victoria, 2021. TOPSCORES. https://www.topscores.co/Vic/vce-school-rank-median-vce/2021/
- (n.d.). VICTORIA SHOPPING CENTRES - MALL LIST, DIRECTIONS, HOURS, MAP, CONTACTS. Australia Shoppings. https://www.australia-shoppings.com/malls-centres/victoria
- (n.d.). DataShare. Victoria State Government Environment, Land, Water and Planning. https://datashare.maps.vic.gov.au/search?q=uuid%3D46bba391-0d67-5bd7-b0bb-bb37945c5c4a
- (P. (2021). Worth it or deserve it? The English Farm. https://theenglishfarm.com/blog/worth-it-or-deserve-it
- (2021). Housing price and sales statistics - Overview. eurostat. https://ec.europa.eu/eurostat/web/housing-price-statistics
- (n.d.). Victorian Electors by Locality, Postcode and Electorates. DataVic. https://discover.data.vic.gov.au/dataset/victorian-electors-by-locality-postcode-and-electorates
- (n.d.). PTV Metro Train Stations. DataVic. https://discover.data.vic.gov.au/dataset/ptv-metro-train-stations
- (n.d.). Vicmap Features - Features of Interest (FOI) Point. Victoria State Government. https://datashare.maps.vic.gov.au/search?md=019d7631-1234-5112-9f21-8f7346647b61
- Koech, K. E. (2021). Web Scraping 1: Scraping Table Data. Medium. https://towardsdatascience.com/web-scraping-scraping-table-data-1665b6b2271c
- (n.d.). Victoria in Future 2019 (VIF2019). Victoria State Government. https://www.planning.vic.gov.au/__data/assets/excel_doc/0027/424386/VIF2019_Pop_Hholds_Dws_ASGS_2036.xlsx
- (n.d.). CRIME & SAFETY IN YOUR AREA. Victoria State Government. https://files.crimestatistics.vic.gov.au/2022-06/Data_Tables_Criminal_Incidents_Visualisation_Year_Ending_March_2022.xlsx
- Lubis, V. (2021). How to Scrape Table from Website using Python. Medium. https://medium.com/analytics-vidhya/how-to-scrape-a-table-from-website-using-python-ce90d0cfb607
- (n.d.). Melbourne Median household income - Weekly income Ranking. SuburbProfile. http://house.speakingsame.com/suburbtop.php?sta=vic&cat=Median%20household%20income&name=Weekly%20income&page=
- A. (2020). Analyzing rate seasonality and ways to save money in the rental market. Github. https://github.com/alexkruczkowski/Rental-Rates-Analysis/blob/master/.ipynb_checkpoints/RentalRatesV1-checkpoint.ipynb
- Mehta, I. (2020). Simple linear regression fit and prediction on time series data with visualization in python. Medium. https://ishan-mehta17.medium.com/simple-linear-regression-fit-and-prediction-on-time-series-data-with-visualization-in-python-41a77baf104c
- SEETO, T. (2020). How much should I spend on rent? Canstar. https://www.canstar.com.au/budgeting/affording-rent-payments/
- (n.d.). Build awesome apps with Google’s knowledge of the real world. Google. https://maps.googleapis.com
- (n.d.). Search Australia's home of property. Domain. https://www.domain.com.au/?mode=rent
