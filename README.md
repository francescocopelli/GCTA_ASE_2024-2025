# GCTA_ASE_2024-2025

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
    docker-compose up --build -d
    ```
    If you want to stop the services run:
    ```sh
    docker-compose down
    ```

4. **Access the application**
    - The application should now be running. You can access it via `http://localhost:8080` for the user services and via `http://localhost:8081` for the admin related operations.

5. **API Documentation**
    - The API documentation can be found in the [doc/openapi.yaml](doc/openapi.yaml) file.

6. **Additional Information**
    - For more details, refer to the [README.md](README.md) and [TODO.md](TODO.md) files.