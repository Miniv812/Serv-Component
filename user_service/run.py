from user_app import create_app
from user_app.grpc_server import start_grpc_server_in_background

app = create_app()

if __name__ == "__main__":
    start_grpc_server_in_background(app)
    app.run(host="0.0.0.0", port=8081)
