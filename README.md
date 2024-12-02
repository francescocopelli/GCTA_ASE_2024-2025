# GCTA ASE 2024-2025

[![CI Pipeline](http://github.com/francescocopelli/GCTA_ASE_2024-2025/actions/workflows/workflow.yaml/badge.svg?branch=main)](http://github.com/francescocopelli/GCTA_ASE_2024-2025/actions/workflows/workflow.yaml)
[![License](http://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Language](http://img.shields.io/github/languages/top/francescocopelli/GCTA_ASE_2024-2025)
## Description
This repository contains the code for GCTA ASE 2024-2025.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Introduction
The GCTA project is a backend system for a gacha game. It uses microservices architecture with Flask and Docker. Core functionalities include user management, authentication, transactions, auctions, and gacha item management. The system is designed to be scalable and maintainable, leveraging the benefits of microservices to isolate different parts of the application for easier development and deployment.

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
    git clone <repository-url>
    cd GCTA_ASE_2024-2025
    ```

2. **Set up the environment**
    - Ensure you have Docker and Docker Compose installed on your machine.
    ```sh
    docker -v
    docker compose version
    ```
3. **Build and run the services**
    ```sh
    docker compose up --build -d
    ```
    If you want to stop the services run:
    ```sh
    docker compose down
    ```

4. **Access the application**
    - The application should now be running. You can access it via `http://localhost:8080` for the user services and via `http://localhost:8081` for the admin related operations.

5. **API Documentation**
    - The API documentation can be found in the [doc/openapi.yaml](doc/openapi.yaml) file.

6. **Additional Information**
    - For more details, refer to the [README.md](README.md) and [TODO.md](TODO.md) files.



## Running on Windows

If you are using Windows and encounter an error such as `/app/shared/start.sh: cannot execute: required file not found` when trying to run `docker compose up`, follow these steps to fix it:

1. Open the `start.sh` file in your text editor.
2. Change the line endings from `CRLF` to `LF`.
    - In VS Code, you can do this by clicking on the `CRLF` button in the bottom-right corner of the editor and selecting `LF`.
3. Save the file and try running `docker compose up` again.

### Explanation

This issue occurs because Windows uses `\r\n` (carriage return and line feed) for line endings, while Unix-based systems (including Docker containers) use `\n` (line feed) only. The extra `\r` character is not recognized by the container and is interpreted as part of the filename, causing the file not to be found.
