# `PickNest`

`PickNest` is a fully backend e-commerce application developed using Flask and SQLAlchemy, designed to facilitate seamless interactions between clients and companies. It offers an API for managing key entities such as clients, addresses, companies, items, orders, and payments. The core functionality of PickNest revolves around linking clients to the products that companies have in stock, enabling efficient stock management and order processing.

The application includes robust features for user account management, allowing both clients and companies to create and manage their accounts with ease. Clients can place orders, while companies can oversee their inventory in real time, with stock levels being adjusted automatically as orders are processed.

Security is a top priority in PickNest, with role-based authorization implemented to ensure that users have appropriate access based on their role (client or company). This prevents unauthorized access and mismatches between account types. Comprehensive security measures have been built into the API, protecting sensitive data and ensuring that operations are carried out with the highest level of integrity.

With endpoints designed for key operations such as account management, order tracking, and inventory control, PickNest ensures that companies can maintain accurate stock records while providing clients with a smooth and secure purchasing experience. The real-time inventory deduction ensures that businesses can manage their products efficiently, improving operational workflows and customer satisfaction.

## Project Structure
├── README.md  
├── api  
│   ├── __init__.py  
│   ├── app.py  
│   └── views  
│       ├── __init__.py  
│       ├── address.py  
│       ├── client.py  
│       ├── company.py  
│       ├── hash_password.py  
│       ├── items.py  
│       ├── login.py  
│       ├── order_items.py  
│       ├── orders.py  
│       ├── payments.py  
│       └── token_auth.py  
├── make_admin.py  
├── models  
│   ├── __init__.py  
│   ├── address.py  
│   ├── basemodel.py  
│   ├── client.py  
│   ├── company.py  
│   ├── items.py  
│   ├── order_items.py  
│   ├── orders.py  
│   ├── payments.py  
│   └── storage.py  
├── requirements.txt  
├── run.py  
└── tests  
    └── api  
        └── views  
            ├── test_address.py  
            └── test_client.py  


## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/PickNest.git
    cd PickNest
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv .picknest
    source .picknest/bin/activate
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Running the Application

1. Set the `PYTHONPATH` environment variable to the root directory of your project:
    ```sh
    export PYTHONPATH=$(pwd)
    ```

2. Run the Flask application:
    ```sh
    flask run
    ```

3. Access the application at `http://127.0.0.1:5000`.

## API Documentation

The API documentation is available via Swagger UI. After running the application, navigate to `http://127.0.0.1:5000/apidocs` to view the API documentation.

## Endpoints

### Client Endpoints

#### Get All Clients

- **URL**: `/clients`
- **Method**: `GET`
- **Description**: Retrieves a list of all clients.
- **Response**:
    ```json
    [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com"
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "email": "jane.smith@example.com"
        }
    ]
    ```

#### Get Client by ID

- **URL**: `/clients/<int:client_id>`
- **Method**: `GET`
- **Description**: Retrieves a single client by ID.
- **Response**:
    ```json
    {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
    ```

### Company Endpoints

#### Sign Up Company

- **URL**: `/companies/sign_up`
- **Method**: `POST`
- **Description**: Sign-up companies to have accounts.
- **Request Body**:
    ```json
    {
        "name": "Company Name",
        "username": "company_username",
        "password": "password",
        "email": "company@example.com",
        "phone_number": "1234567890",
        "address1": "123 Main St",
        "address2": "Suite 100",
        "city": "Anytown",
        "state": "CA",
        "zip": "12345",
        "country": "USA"
    }
    ```
- **Response**:
    ```json
    {
        "message": "Company registered successfully"
    }
    ```

#### Login Company

- **URL**: `/companies/login`
- **Method**: `POST`
- **Description**: Login route for companies.
- **Request Body**:
    ```json
    {
        "username": "company_username",
        "password": "password"
    }
    ```
- **Response**:
    ```json
    {
        "message": "Company logged in successfully",
        "token": "jwt_token"
    }
    ```

#### Get All Companies

- **URL**: `/companies`
- **Method**: `GET`
- **Description**: Retrieve list of all companies.
- **Response**:
    ```json
    [
        {
            "public_id": "uuid",
            "name": "Company Name",
            "username": "company_username",
            "email": "company@example.com",
            "phone_number": "1234567890",
            "address1": "123 Main St",
            "address2": "Suite 100",
            "city": "Anytown",
            "state": "CA",
            "zip": "12345",
            "country": "USA",
            "role": "company"
        }
    ]
    ```

#### Get Company by ID

- **URL**: `/companies/<company_id>`
- **Method**: `GET`
- **Description**: Retrieve a company by ID.
- **Response**:
    ```json
    {
        "public_id": "uuid",
        "name": "Company Name",
        "username": "company_username",
        "email": "company@example.com",
        "phone_number": "1234567890",
        "address1": "123 Main St",
        "address2": "Suite 100",
        "city": "Anytown",
        "state": "CA",
        "zip": "12345",
        "country": "USA",
        "role": "company"
    }
    ```

#### Create a New Company

- **URL**: `/companies`
- **Method**: `POST`
- **Description**: Create a new company.
- **Request Body**:
    ```json
    {
        "name": "Company Name",
        "username": "company_username",
        "password": "password",
        "email": "company@example.com",
        "phone_number": "1234567890",
        "address1": "123 Main St",
        "address2": "Suite 100",
        "city": "Anytown",
        "state": "CA",
        "zip": "12345",
        "country": "USA"
    }
    ```
- **Response**:
    ```json
    {
        "public_id": "uuid",
        "name": "Company Name",
        "username": "company_username",
        "email": "company@example.com",
        "phone_number": "1234567890",
        "address1": "123 Main St",
        "address2": "Suite 100",
        "city": "Anytown",
        "state": "CA",
        "zip": "12345",
        "country": "USA",
        "role": "company"
    }
    ```

#### Update a Company

- **URL**: `/companies/<company_id>`
- **Method**: `PUT`
- **Description**: Updates a company.
- **Request Body**:
    ```json
    {
        "name": "Updated Company Name",
        "email": "updated@example.com",
        "phone_number": "0987654321",
        "address1": "456 Another St",
        "address2": "Suite 200",
        "city": "Othertown",
        "state": "NY",
        "zip": "67890",
        "country": "USA"
    }
    ```
- **Response**:
    ```json
    {
        "public_id": "uuid",
        "name": "Updated Company Name",
        "username": "company_username",
        "email": "updated@example.com",
        "phone_number": "0987654321",
        "address1": "456 Another St",
        "address2": "Suite 200",
        "city": "Othertown",
        "state": "NY",
        "zip": "67890",
        "country": "USA",
        "role": "company"
    }
    ```

#### Delete a Company

- **URL**: `/companies/<company_id>`
- **Method**: `DELETE`
- **Description**: Delete a company by ID.
- **Response**:
    ```json
    {
        "message": "Company deleted successfully"
    }
    ```

## Testing

To run the tests, use the following command:
```sh
python3 -m unittest <path/to/test>