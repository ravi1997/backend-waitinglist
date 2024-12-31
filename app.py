from app import create_app

some_app = create_app()

if __name__ == "__main__":
	some_app.run("0.0.0.0",debug=True)