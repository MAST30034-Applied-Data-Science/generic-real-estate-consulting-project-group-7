# Group7-Sprint 4&5-Summary Notebook

# Table of Content
- [Group7-Sprint 4&5-Summary Notebook](#group7-sprint-45-summary-notebook)
- [Table of Content](#table-of-content)
  - [Scraping data](#scraping-data)
  - [Preprocessing data](#preprocessing-data)
  - [Modelling](#modelling)
    - [Linear Regression](#linear-regression)
    - [Random Forest](#random-forest)
    - [Naive Bayes](#naive-bayes)
    - [Pyspark - Gradient Boost Tree Regression](#pyspark---gradient-boost-tree-regression)
    - [Pyspark - XGBoost](#pyspark---xgboost)
    - [Liveable (ideas)](#liveable-ideas)
    - [Affordble (ideas)](#affordble-ideas)
    - [Predictions](#predictions)


## Scraping data
  - Finish scrape [domain dataset]('https://www.domain.com.au/') as our internal data
  - Finish download all external data

## Preprocessing data
  - Finish preprocessing internal dataset
    - remove postcode not within metro melbourne 
    - remove postcode with less than 10 property
    - remaining 12127 properties with 180 suburbs
![Drag Racing](../plots/meeting_minutes/sprint4-sample.jpeg)

  - Finish preprocessing external dataset
    - the duration to closest
      - public service
      - care facility
      - shopping center
      - train station
      - hospital
      - CBD
      - emergency services
    - property and Elctor count
    - crime rate
    - income
    - school information calculated by ranking
![Drag Racing](../plots/meeting_minutes/summary-internal-features.png)

  - Merge internal and external features together


## Modelling 
**aims to provide students with an opportunity to help predict rental prices for both residential properties and apartments throughout Victoria, Australia**

1. What are the most important internal and external features in predicting rental prices?
2. What are the most liveable and affordable suburbs according to your chosen metrics?
3. What are the top 10 suburbs with the highest predicted growth rate?
4. Forecasting the rental properties for the next 3 years


### Linear Regression
  - We would like to try the linear regression with categorical version of model data, but the ordinal data can not satisfy the assumption of linear regression. If we use one-hot encoding, the number of feature may increase to at least 60. So we decide not to use linear regression for feature selection.

### Random Forest
  - assumption: the data feature is continuous and predicted label is also continuous
  - we see that there are some discrete values in model data, that is, categorical features. In order to meet the assumption, we turn them into continuous values through data preprocessing. In addition, the nominal data type of property type is converted into one-hot encoding through preprocessing, so now the input data meets the assumption. At this point, we can fit the data with RF
  - we used Grid Search to find the best parameter of 700, and then we found that the other Max features we used, whether SQRT or log, they all worked about the same
  - Random Forest does not have strong assumptions compared to linear regression, LR requires a trend of the dependent variable between its independent variable and the dependent variable, while RF does not
  - Because the housing market itself is very unstable, that is, there will be many outlier, RF is an emveding model, so its robust ability is very strong, so it will be less affected by the outlier of the housing price.

**From the summary of the model, we can see that the factors that have a greater impact on the house price are the number of bedrooms and geographical location, followed by the number of bathrooms**
![Drag Racing](../plots/meeting_minutes/summary-rf.png)
![Drag Racing](../plots/meeting_minutes/summary-rf-1.png)

### Naive Bayes
   - We tried **GaussianNB** and **CategoricalNB**, since NB can only do classfication, the so we convert price to categorical with super cheap \ cheap \ expansive \ super expensive
   - Both use stratified k fold
   - Problems:
     - By checking pearson correlation, some features are dependent on each other
     - By checking permutation feature imoportance, find that some features are not important at all
     - model has high variance
![Drag Racing](../plots/meeting_minutes/summary-nb-1.png)
![Drag Racing](../plots/meeting_minutes/summary-nb-2.png)

### Pyspark - Gradient Boost Tree Regression
![Drag Racing](../plots/meeting_minutes/summary-gbt.png)

### Pyspark - XGBoost
   - RMSE and R2 score

![Drag Racing](../plots/meeting_minutes/summary-xgb-1.png)
   - Top 15 importance features based on F score

![Drag Racing](../plots/meeting_minutes/summary-xgb-2.png)
   - Top 15 importance features based on gain

![Drag Racing](../plots/meeting_minutes/summary-xgb-3.png)

### Liveable (ideas)
   - According to https://auo.org.au/portal/metadata/urban-liveability-index/, the Liveability Index is a composite score based on measures related to aspects of liveability including Social Infrastructure, Walkability, Public Transport, Public Open Space, Housing Affordability, and Local Employment.
   - We would like to choose 5 metrics:
     - Social Infrastructure: Number of Social Infrastructure in this postcode
     - Walkability: The duration between property and Social Infrastructure
     - Public Transport: The duration between property and train station
     - Housing Affordability: Rent proportion of income of each person
     - Local Employment: Median income of each postcode
   - These five metrics are graded according to ranking, with a maximum of 20 points for each metric and a maximum of 100 points in total. For example, if we sort the duration, the most recent top 10% get 20 points, 10%-20% get 18 points, 20%-30% get 16 points...the last 20% get no points. Then after the score of each property comes out, follow the postcode group by to get the ranking of each suburb.

### Affordble (ideas)
   - According to https://www.canstar.com.au/budgeting/affording-rent-payments/, it recommends that people should not spend more than 30% of gross income on rent
   - Therefore we would like to use weekly_rent/weekly_income to determine whether this subrub is affordable Since different property may have different number of bedroom, we assumed that the number of bedroom is number of people live in this house and we assumed that they will split the rent bill
   - So we use the total_price_of_property/number_of_bedroom to get the cost of rent od each people in each property, then we use this to divide median weekly income of the postcode that property located to get the rent_proportion
   - After we calculate the rent_proportion:
     - Delete the suburb which contain the unaffordable property
     - For the suburb which do not contain the unaffordable property, we would like to group by by postcode by mean of the rent_proportion
     - Sort the group by data, get the top ten affordable suburb which have the less rent_proportion

![Drag Racing](../plots/meeting_minutes/summary-affordable.jpeg)

### Predictions
   - we wanna apply timeseries model to forecasting the rental properties for the next 3 years, but the data we only get is 2022
   - we search from the website https://www.dhhs.vic.gov.au/past-rental-reports, we can get the past years quarterly rent data
![Drag Racing](../plots/meeting_minutes/summary-timeseries.png)
   - still modelling ARIMA and LSTM
   - Is there any other method that we can use to prediction price???