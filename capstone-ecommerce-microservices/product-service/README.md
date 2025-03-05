# Product Service Microservice

Part of the E-commerce Microservices System, this service handles product management and inventory control.

## 🚀 Features

- Product CRUD operations
- Stock management
- Low stock alerts
- Snowflake database integration
- Comprehensive error handling and logging

## 🛠 Tech Stack

- Python 3.11
- Django REST Framework
- Snowflake Database
- Docker

## 📋 Prerequisites

- Python 3.11+
- Docker
- Snowflake Account

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=TRIAL_DB
SNOWFLAKE_SCHEMA=TRIAL_SCMA
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
```

## 📂 Project Structure

```markdown
product-service/
├── product_prj/
│ ├── product_app/
│ │ ├── models.py
│ │ ├── views.py
│ │ ├── serializers.py
│ │ ├── urls.py
│ │ └── tests.py
│ ├── requirements.txt
│ └── manage.py
├── Dockerfile
└── README.md
```
