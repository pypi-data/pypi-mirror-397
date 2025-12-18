from environs import env

from bakit.app import create_app

env.read_env()
app = create_app()


PORT = env.int("LOCALHOST_PORT", 8000)

if __name__ == "__main__":
    app.run(
        host="localhost",
        port=PORT,
        debug=True,
        auto_reload=True,
    )
