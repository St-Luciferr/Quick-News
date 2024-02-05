import psycopg2

from sshtunnel import SSHTunnelForwarder


# Replace these values with your actual SSH and database connection details
ssh_params = {
    "ssh_address_or_host": "18.217.209.236",
    "ssh_username": "ubuntu",
    "ssh_pkey": "/home/saurab/Downloads/quickfox/rpa-dev.pem",
    "remote_bind_address": ("127.0.0.1", 5432),
}

# Replace these values with your actual database connection details
db_params = {
    "host": "localhost",
    "port": 5432,
    "database": "quicknews",
    "user": "test",
    "password": "password",
}


conn = None

try:
    # Create an SSH tunnel
    with SSHTunnelForwarder(**ssh_params) as tunnel:
        print(f"Tunnel established at localhost:{tunnel.local_bind_port}")

        # Establish a connection to the PostgreSQL server through the SSH tunnel
        conn = psycopg2.connect(
            host="localhost",
            port=tunnel.local_bind_port,
            user=db_params["user"],
            database=db_params["database"],
            password=db_params["password"],
        )

        # Create a cursor object
        cursor = conn.cursor()

        # Execute a simple query to test the connection
        cursor.execute("SELECT version()")

        # Fetch and print the result
        result = cursor.fetchone()
        print("PostgreSQL server version:", result[0])

except psycopg2.Error as e:
    print("Unable to connect to the database.")
    print(e)

finally:
    # Close the cursor and connection
    if conn:
        conn.close()
        print("Connection closed.")
