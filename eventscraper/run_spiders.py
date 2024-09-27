import subprocess
import os
import sqlite3


def main():
    processes = []
    os.makedirs("output", exist_ok=True)  # set exist_ok to True

    db_file = 'C:\\Users\\jacob\\PycharmProjects\\CanooEventScraper\\canooevents.db'
    con = sqlite3.connect(db_file)  # creates the connection
    cur = con.cursor()  # creates the cursor, used to execute commands on db

    cur.execute("""SELECT domain, venue_name_hardcode FROM domain_logic""")
    rows = cur.fetchall()

    for domain_row in rows:  # domains in the database should be https://<rest of the url>
        domain = domain_row[0]  # extract the individual domain
        domain_name = domain_row[1]  # get the domain for file naming purposes
        processes.append(  # runs a process as if user was doing them 1 by 1 in the terminal
            subprocess.Popen(  # subprocess allows for all these spiders to be run simultaneously
                [
                    "scrapy",
                    "crawl",
                    "testing",  # spider name
                    "-a",
                    f"url={domain}",
                    "-O",
                    f"output/csv/{domain_name}.csv"
                ]  # change csv and .csv to json and .jsonl in both spots to export as csv
            )
        )

    for process in processes:
        process.wait()


if __name__ == "__main__":  # entry point for the script, allows it to be run
    main()
