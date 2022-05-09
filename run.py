from anki import App, AnkiDB
import sys

if __name__ == "__main__":
    app = App(db=AnkiDB(dbname=input("Enter the name of the database: ")))
    app.run()
    print("Exiting...")
    sys.exit(0)
