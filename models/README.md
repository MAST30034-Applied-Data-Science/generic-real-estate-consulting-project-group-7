# Modelling Specification

## Table of Content
- [Modelling Specification](#modelling-specification)
  - [Table of Content](#table-of-content)
  - [General Specification](#general-specification)
  - [Code Running Instructions](#code-running-instructions)


## General Specification
Mian Problem: determine the appropriate level of rent an online real estate company should be listing their properties, as well as which properties are most likely to increase in the next five years

- Question 1: What are the most important internal and external features in predicting rental prices?
  - XGBoost performs the best among those models
  - The most important internal features are bathrooms, bedrooms and parking
  - The most important external features are the duration to CBD, crime rate and income

- Question 2: What are the top 10 suburbs with the highest predicted growth rate?
  - We create a simple linear regression line for each suburb’s time-series data, visualize it, and get the slope and intercept values. Therefore, we can predict the median rental price for each suburb. For visualization, we also predict the rental price in 2023 and 2024. 
  - After we predict the next 3 years  median rental price by postcode, based on 2000-2022 median rental price , we can calculate the 3 year growth rate by this formula

- Question 3: What are the most liveable and affordable suburbs according to your chosen metrics?
  - [3040, 3078, 3079, 3144, 3052, 3056, 3121, 3122, 3101, 3039]

## Code Running Instructions
```
Question 1.ipynb   # importance of features
Question 2.ipynb   # output 3 years rent prediction
Question 3.ipynb   # liveable and affordable suburbs
```
