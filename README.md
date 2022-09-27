# Generic Real Estate Consulting Project

# Table of contents
- [Generic Real Estate Consulting Project](#generic-real-estate-consulting-project)
- [Table of contents](#table-of-contents)
  - [Project Specification:](#project-specification)
  - [Group Information](#group-information)
  - [Dependencies](#dependencies)
  - [**Code Running Instructions**](#code-running-instructions)

## Project Specification:

This project aims to ...

## Group Information
**Group name:** Group 7
    
| Student Name | Student ID | Email |
| ---- | ---- | ---- |
| QUZIHAN WU | 1078419 | quzihanw@student.unimelb.edu.au |
| YINAN LI | 1173947 | yinan3@student.unimelb.edu.au | 
| XINGYAO WANG | 1179108 |  |
| ZIXUAN GUO | 1124606 |  |
| ZONGCHAO XIE | 1174047 |  |

## Dependencies
**[MANDATORY]**

The project is conducted with `python` environment, please install required dependencies before executing any notebooks.
```bash
# install dependencies
pip install -r requirements.txt
```

## **Code Running Instructions**

To recreate the result, please run jupyter notebooks with the following order:
1. Download required data
```
# download domain website data
|-- notebooks
  |-- domain-website-download
    |-- download.ipynb 

# download all external data
|-- notebooks
  |--external-data-download
    |-- download.ipynb
```
2. Data Preprocessing
```
# preprocessing and join all external data as external-features
|-- notebooks
  |-- preprocessing
    |-- join

# preprocessing external-features
|-- notebooks
  |-- preprocessing
    |-- external-features-preprocessing
```
3. Merge Results

4. Analyze and Modelling

