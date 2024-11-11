# make a bash script that take the database into the docker volume and export it in /dbdata/user_db/user.db

docker cp gcta_ase_2024-2025-db-manager-1:/app/user.db ./dbdata/users_db/user.db
