# GCTA ASE 2024-2025

[![CI Pipeline](http://github.com/francescocopelli/GCTA_ASE_2024-2025/actions/workflows/workflow.yaml/badge.svg?branch=main)](http://github.com/francescocopelli/GCTA_ASE_2024-2025/actions/workflows/workflow.yaml)
[![License](http://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Language](http://img.shields.io/github/languages/top/francescocopelli/GCTA_ASE_2024-2025)
## Description
This repository contains the code for GCTA ASE 2024-2025.
[Final Report](https://github.com/francescocopelli/GCTA_ASE_2024-2025/blob/1fe9747da78711405ee0458d41c115b4c1aee9af/docs/Final_Report.pdf)
## Introduction
The GCTA project is a backend system for a gacha game. It uses microservices architecture with Flask and Docker.

Core functionalities include user management, authentication, transactions, auctions, and gacha item management.

The system is designed to be scalable and maintainable, leveraging the benefits of microservices to isolate different parts of the application for easier development and deployment.

### Key Features:
- **User Management**: Handles user registration, login, and profile management.
- **Authentication**: Secure authentication mechanisms using JWT tokens.
- **Transactions**: Manages user transactions, including in-game purchases and currency balance updates.
- **Auctions**: Facilitates the creation and management of auctions for gacha items.
- **Gacha Item Management**: Manages the inventory of gacha items, including adding, updating, and retrieving items.

### Technologies Used:
- **Flask**: A lightweight WSGI web application framework in Python.
- **Docker**: Containerization platform to package and deploy microservices.
- **MySQL**: Database for storing application data.
- **JWT**: JSON Web Tokens for secure authentication.
- **Requests**: Python HTTP library for making API requests.





## Get Started

In order to start using the GCTA game, you have to:

1. **Clone the repository**
    ```sh
    git clone https://github.com/francescocopelli/GCTA_ASE_2024-2025.git
    cd GCTA_ASE_2024-2025
    ```
2. **Preliminary step**

For compatibility reasons you will have to run a script in order to make sure that the project can run without any issues if you are using either Windows or Linux.    This script will automatically convert all `.sh` files in the project from `CRLF` to `LF`.
```sh
   python tool.py
```

You should see in the output result something such as:

```sh
    [SUCCESS] Converted CRLF to LF for: <file>
```
##### Explanation
This issue occurs because Windows uses `\r\n` (carriage return and line feed) for line endings, while Unix-based systems (including Docker containers) use `\n` (line feed) only. The extra `\r` character is not recognized by the container and is interpreted as part of the filename, causing the file not to be found.


3. **Set up the environment**
    - Ensure you have Docker and Docker Compose installed on your machine.
    ```sh
    docker -v
    docker compose version
    ```
4. **Build and run the services**
    ```sh
    docker compose up --build -d
    ```
    If you want to stop the services run:
    ```sh
    docker compose down
    ```

5. **Access the application**
    - The application should now be running. You can access it via `https://localhost:8080` for the user services and via `https://localhost:8081` for the admin related operations.

6. **API Documentation**
    - The API documentation can be found in the [docs/API_admin.yaml](docs/API_admin.yaml) file for the admins endopoints and in the [docs/API_player.yaml](docs/API_player.yaml) for the user endpoints.

## Bandit
Bandit is a static analysis tool to find potential security issues in Python code. It runs a series of checks on each file and reports any vulnerabilities.

To run Bandit, use the following command:
```sh
bandit -r . -x ./.venv/,./test_locust/,./mockup_test/,./locustfile.py -s=B501
```
### Command explanation
1. -r .: Recursively scans all directories and files in the project.
2. -x : Excludes the folders used for the tests code, which would give false positives.
3. -s=B501: Excludes the B501 check (request_with_no_cert_validation) to avoid false positives, as we added the verify=False to remove the check on the certificates used with requests, as they are self signed.

## Postman tests
Newman is a command-line tool to run Postman collections. This command will run the tests defined in the GCTA_Tests.postman_collection.json collection using the gcta_env.postman_environment.json environment. The --insecure option allows ignoring SSL certificate issues.
To run the tests with Postman, use the following commands:
1. First, make sure that you have installed newman on your system:
    ```sh
    sudo npm install -g newman
    ```
2. Once you have installed newman run the following command to use the collections for testing:
    ```sh
    newman run ./postman_tests/GCTA_Tests.postman_collection.json -e ./postman_tests/gcta_env.postman_environment.json --insecure
    ```

## Locust tests

Locust is a performance testing tool that allows you to define user behavior and simulate multiple users interacting with your application.

### Running Locust tests

To run Locust tests, follow these steps:

1. **Install Locust**:
   Make sure you have Locust installed on your system. You can install it using pip:
   ```sh
        pip install locust
   ```
2. **Run Locust from the command line**:
    Use the following command to run Locust, specifying the host, the number of users to spawn, and the spawn rate (users per second):
    ```sh
        locust -f locustfile.py --host https://localhost:8080 --users 20 --spawn-rate 5
    ```
    This is going to make at most 20 concurrent users spawned 5 every seconds. If you want to spawn more users you have to change the 2 values.
3. **Start the tests**: 
    You should now see on http://localhost:8089 the locust webpage where you can start the tests and see the results in terms of performance on different loads.

## Isolation tests
Isolation tests have been used to test individual services in absence of the database and other service dependencies. These are the genaral steps: 
1. Navigate to the root directory of the project
2. Build the Docker image for the service using the provided `dockerfile_test` (used for testing purposes instead of the main `dockerfile`).
3. Run the Docker container for the service in detached mode, naming it appropriately.
4. Execute the Newman test for the service using the `GCTA_Isolation_Tests.postman_collection.json` and the corresponding environment file.

To execute the isolation tests for each service use the following commands. Every time you want to 
test another one remember to remove the previous one. The test uses port 5000, if you change it you will have to change it also on all the tests.


#### Auction Service
```sh

    docker build -t mock_auction -f ./auction_mockup_test.dockerfile .
    docker run -d -p 5000:5000 --name auction_mockup_test mock_auction
    newman run ./isolation_tests_postman/GCTA_Isolation_Tests.postman_collection.json --folder "Auctions" --environment ./isolation_tests_postman/gcta_mock.postman_environment.json --insecure
```
#### Gacha Service
```sh

    docker build -t gacha-mock -f gacha_mockup_test.dockerfile .
    docker run -d -p 5000:5000 --name gacha-mock-container gacha-mock
    newman run ./isolation_tests_postman/GCTA_Isolation_Tests.postman_collection.json --folder "Gachas" --environment ./isolation_tests_postman/gcta_mock.postman_environment.json --insecure
```
#### Player Service
```sh
    docker build -t users-mock -f users_mockup_test.dockerfile .
    docker run -d -p 5000:5000 --name users-mock-container users-mock
    newman run ./isolation_tests_postman/GCTA_Isolation_Tests.postman_collection.json --folder "Player" --environment ./isolation_tests_postman/gcta_mock.postman_environment.json --insecure
```
#### Transaction Service
```sh
    docker build -t transaction-mock -f transaction_mockup_test.dockerfile .
    docker run -d -p 5000:5000 --name transaction-mock-container transaction-mock
    newman run ./isolation_tests_postman/GCTA_Isolation_Tests.postman_collection.json --folder "Transactions" --environment ./isolation_tests_postman/gcta_mock.postman_environment.json --insecure
```
#### Player Auth Service
```sh
    docker build -t player-auth-mock -f users_auth_mockup_test.dockerfile .
    docker run -d -p 5000:5000 --name player-auth-mock-container player-auth-mock
    newman run ./isolation_tests_postman/GCTA_Isolation_Tests.postman_collection.json --folder "Player auth" --environment ./isolation_tests_postman/gcta_mock.postman_environment.json --insecure
```

#### Admin Auth Service
```sh
    docker build -t admin-auth-mock -f admin_auth_mockup_test.dockerfile .
    docker run -d -p 5000:5000 --name admin-auth-mock-container admin-auth-mock
    newman run ./isolation_tests_postman/GCTA_Isolation_Tests.postman_collection.json --folder "Admin_auth" --environment ./isolation_tests_postman/gcta_mock.postman_environment.json --insecure
```
#### Db manager Service
```sh
docker build -t dbm-mock -f dbm_mockup_test.dockerfile .
docker run -d -p 5000:5000 --name dbm-mock-container dbm-mock
newman run ./isolation_tests_postman/GCTA_Isolation_Tests.postman_collection.json --folder "Db-manager" --environment ./isolation_tests_postman/gcta_mock.postman_environment.json --insecure
```

#### Admin Service
```sh
docker build -t admin-mock -f admin_mockup_test.dockerfile .
docker run -d -p 5000:5000 --name admin-mock-container admin-mock
newman run ./isolation_tests_postman/GCTA_Isolation_Tests.postman_collection.json --folder "Admin" --environment ./isolation_tests_postman/gcta_mock.postman_environment.json --insecure
```
