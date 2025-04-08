Main Features:
1.User Management Service
-------------------------------
Expose a set of RESTful APIs for managing users (registration, authentication, profile updates, and retrieval).
Implement JWT-based authentication and role-based access control (RBAC).
Store user data in a PostgreSQL database using SQLAlchemy with optimized queries and indexing.
2.Notification Service
--------------------------------
Listens for new user registrations and triggers a mock notification (e.g., email or SMS).
Service communication should be implemented using either:
Asynchronous REST API calls
Event-driven messaging via RabbitMQ/Kafka


Prerequesites
----------------------
1. install python
2.. pip install fastapi uvicorn sqlalchemy pydantic aio_pika psycopg2-binary
    FastAPI: The web framework to build APIs.
    SQLAlchemy: ORM for database interactions.
    aio_pika: Asynchronous RabbitMQ client.
    psycopg2-binary: PostgreSQL adapter for Python.
3.  PostgreSQL, RabbitMQ installation

models.py
  --->ThE file contains schema for a User model using SQLAlchemy which is an ORM library
database.py
  -->The code in this file is for configuring the connection between FastAPI application and the PostgreSQL database using SQLAlchemy
  -->Generates the necessary tables (based on the models defined in models.py) in the connected PostgreSQL database.
main.py
  ----->The code defines a FastAPI application that handles user registration, login, profile retrieval, and profile update with integration to a PostgreSQL database using SQLAlchemy. 
  ----->uses RabbitMQ to publish messages when a new user is registered
auth.py
   ---->auth.py file contains functions for password hashing, token creation, and token decoding for user authentication.
