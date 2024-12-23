import os
import sys
import subprocess
import pandas as pd
import json
import mysqlx
from datetime import datetime


from dotenv import load_dotenv

load_dotenv()
ROOT = subprocess.check_output("git rev-parse --show-toplevel", shell=True).decode('utf-8').strip()
OS = sys.platform
if OS != 'linux' and OS != 'darwin':
    raise Exception('Unsupported OS')


def install_mysql() -> bool:
    """
    choosing default installation (not secure)
    run mysql_secure_installation for secure installation
    """
    # if already installed, return
    cmd_test = ['mysql', '--version']

    if OS == "linux":
        cmd_test.insert(0, "sudo")
        result = subprocess.run(cmd_test, check=True)
        if result.returncode == 0:
            print("MySQL is already installed.")
            return True
        else:
            print("MySQL is not installed. Installing MySQL...")
            # install mysql if not installed and check status to verify
            try:
                # subprocess.run(['sudo', 'apt', 'update'], check=True)
                subprocess.run(['sudo', 'apt', 'install', '-y', 'mysql-server'], check=True)
                subprocess.run(['sudo', 'systemctl', 'status', 'mysql'], check=True)
                print("MySQL installation completed.")
                return True
            except Exception as e:
                print(f"Error installing mysql: {str(e)}")
                return False
    elif OS == 'darwin':
        result = subprocess.run(cmd_test)
        if result.returncode == 0:
            print("MySQL is already installed.")
            return True
        else:
            print("MySQL is not installed. Installing MySQL...")
            try:
                subprocess.run(['brew', 'install', 'mysql'], check=True)
                print("MySQL installation completed.")
                return True
            except Exception as e:
                print(f"Error installing mysql: {str(e)}")
                return False
    else:
        print("Unsupported OS")
        return False

def launch_server() -> bool:
    if OS == "linux":
        try:
            subprocess.run(['sudo', 'systemctl', 'start', 'mysql'], check=True)
            print("MySQL server started successfully on Linux.\n")
            return True
        except Exception as e:
            print(f"Error starting MySQL server on Linux: {str(e)}")
            return False
    elif OS == 'darwin':
        try:
            subprocess.run(['brew', 'services', 'start', 'mysql'], check=True)
            print("MySQL server started successfully on macOS.\n")
            return True
        except Exception as e:
            print(f"Error starting MySQL server on macOS: {str(e)}")
            return False
    else:
        print("Unsupported OS")
        return False

def spinup_mysql_server() -> bool:
    if not install_mysql():
        print("Error installing mysql")
        return False

    if not launch_server():
        print("Error launching mysql server")
        return False

    return True

def create_session(db_name: str = None) -> object:
    """
    create mysql server session
    can create a database without giving db_name
    and call later with db_name to connect to the database
    returns the session object (open connection)
    """
    conn_params = {}
    conn_params["host"] = str(os.getenv("MYSQL_HOST", "localhost"))
    conn_params["port"] = int(os.getenv("MYSQL_PORT", "33060"))
    conn_params["user"] = str(os.getenv("MYSQL_USER", "root"))
    conn_params["password"] = str(os.getenv("MYSQL_PASSWORD", ""))

    try:
        session = mysqlx.get_session(**conn_params)
        schema = None
        if db_name:
            schema = session.get_schema(db_name)
            # WARNING: we intentionally select the database for the session
            # this will propogate to chained functions but not to new sessions
            session.sql(f"USE {db_name}").execute()  # Ensure the database is selected

        # print(f'{db_name = }\t{session = }\t{schema = }')
        return session, schema
    except Exception as e:
        print(f"Error connecting to mysql as '{conn_params['user']}'@'{conn_params['host']}'\n{str(e)}")
        # return None, None
        sys.exit(1)

def create_db(db_name: str = "grimrepor_db") -> bool:
    """
    create a new database
    ok if the database already exists
    """
    session, _ = create_session()
    try:
        session.sql(f"CREATE DATABASE IF NOT EXISTS {db_name}").execute()
        print(f"Database '{db_name}' is active.")
    except mysqlx.DatabaseError as e:
        if "schema exists" in str(e).lower():
            print(f"Database {db_name} already exists.")
            return True
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        return False
    finally:
        session.close()

def show_databases() -> bool:
    session, _ = create_session()
    try:
        print(f"\nDatabases: {session.get_schemas()}\n")
        if session:
            session.close()
        return True
    except Exception as e:
        print(f"Error showing databases: {str(e)}")
        return False
    finally:
        if session: session.close()

def show_all_tables(db_name: str = "grimrepor_db") -> bool:
    """
    show all tables in the database
    """
    session, schema = create_session(db_name)
    if not session: return False
    try:
        print(f"Tables in {db_name = }\n")
        _ = [ print(f'  {table.get_name()}') for table in schema.get_tables() ]
        print()
        session.close()
        return True
    except Exception as e:
        print(f"Error showing tables: {str(e)}")
        return False
    finally:
        session.close()

def show_table_columns(table_name: str, db_name: str = "grimrepor_db") -> bool:
    session, _ = create_session(db_name)
    if not session: return False
    print(f"\nColumns in table '{table_name}'\n")
    try:
        result = session.sql(f"SHOW COLUMNS FROM {table_name}").execute()
        for col in result.fetch_all():
            print(f'  {col}')
        print()
        return True
    except Exception as e:
        print(f"Error showing table columns: {str(e)}")
        return False
    finally:
        session.close()

def show_table_contents(table_name: str, db_name: str = "grimrepor_db", limit_num: int = None) -> bool:
    """
    SELECT * FROM table_name;
    option to limit the number of rows returned
    shows all columns
    """
    session, schema = create_session(db_name)
    if not session: return False

    try:
        print(f"Contents of {table_name}\n")
        result = None
        try:
            if limit_num is None:
                result = schema.get_table(table_name).select().execute()
            else:
                result = schema.get_table(table_name).select().limit(limit_num).execute()
        except Exception as e:
            print(f"Error selecting from table: {str(e)}")
            return False

        for row in result.fetch_all():
            print(row)
        return True

    except Exception as e:
        print(f"Error showing table contents: {str(e)}")
        return False
    finally:
        session.close()

def drop_table(table_name: str, db_name: str = "grimrepor_db") -> bool:
    """
    drop a table from the database
    be careful with this command as it will delete a table
    """
    session, _ = create_session(db_name)
    try:
        session.sql("SET FOREIGN_KEY_CHECKS = 0").execute()  # Disable foreign key checks
        session.sql(f"DROP TABLE IF EXISTS {table_name}").execute()
        print(f"Table {table_name} dropped successfully.")
        return True
        session.sql("SET FOREIGN_KEY_CHECKS = 1").execute()  # Re-enable foreign key checks
    except Exception as e:
        print(f"Error dropping table: {str(e)}")
        return False
    finally:
        if session: session.close()

def drop_all_tables(db_name: str = "grimrepor_db") -> bool:
    """
    drop all of the tables
    find all the tables in the database
    then drop them one by one
    """
    ans = input("Are you sure you want to drop all tables? (y/n): ")
    if ans.lower() != 'y':
        print("Tables not dropped.")
        return False

    session, schema = create_session(db_name)
    if not session: return False

    try:
        tables = schema.get_tables()
        session.sql("SET FOREIGN_KEY_CHECKS = 0").execute()  # Disable foreign key checks
        for table in tables:
            table_name = table.get_name()
            session.sql(f"DROP TABLE IF EXISTS {table_name}").execute()
            print(f"Table {table_name} dropped successfully.")
        session.sql("SET FOREIGN_KEY_CHECKS = 1").execute()  # Re-enable foreign key checks
        return True
    except Exception as e:
        print(f"Error dropping tables: {str(e)}")
        return False
    finally:
        session.close()

def delete_data_from_table(table_name: str, db_name: str = "grimrepor_db") -> bool:
    """
    delete all data from a table
    keep column headers
    """
    session, _ = create_session(db_name)
    if not session: return False

    try:
        session.sql(f"TRUNCATE TABLE {table_name}").execute()
        print(f"Data deleted from table {table_name}.")
        return True
    except Exception as e:
        print(f"Error deleting data from table: {str(e)}")
        return False
    finally:
        session.close()


create_table_dict = {
    "papers_and_code_linked": """
    CREATE TABLE IF NOT EXISTS papers_and_code_linked (
        id INT AUTO_INCREMENT PRIMARY KEY,
        paper_url VARCHAR(255) NOT NULL UNIQUE,
        paper_title VARCHAR(255) NOT NULL UNIQUE,
        paper_arxiv_id VARCHAR(255) NOT NULL UNIQUE,
        paper_url_abs VARCHAR(255) NOT NULL UNIQUE,
        paper_url_pdf VARCHAR(255) NOT NULL UNIQUE,
        repo_url VARCHAR(255),
        is_official BOOLEAN,
        mentioned_in_paper BOOLEAN,
        mentioned_in_github BOOLEAN,
        framework VARCHAR(255)
    );""",

    "paper_repo_info_reqs": """
    CREATE TABLE IF NOT EXISTS paper_repo_info_reqs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        paper_title VARCHAR(255) NOT NULL,
        paper_url VARCHAR(255) NOT NULL,
        paper_arxiv_id VARCHAR(255) NOT NULL,
        repo_url VARCHAR(255) NOT NULL,
        is_official BOOLEAN NOT NULL,
        framework VARCHAR(255) DEFAULT NULL,
        readme_url VARCHAR(255) DEFAULT NULL,
        requirements_url VARCHAR(255) DEFAULT NULL,
        requirements_last_commit_date DATE DEFAULT NULL,
        most_prominent_language VARCHAR(255) DEFAULT NULL,
        stars INT DEFAULT 0,
        last_commit_date DATE DEFAULT NULL,
        contributors VARCHAR(1000),
        requirements MEDIUMTEXT
    );""",

    # original fields:
    # "Title", "Link", "Author Info", "Abstract", "Tasks", "GitHub Link", "Star Count"
    "papers_data": """
    CREATE TABLE IF NOT EXISTS papers_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        paper_url VARCHAR(255) NOT NULL,
        author_info VARCHAR(255) DEFAULT NULL,
        abstract TEXT,
        tasks VARCHAR(255) DEFAULT NULL,
        github_url VARCHAR(255) DEFAULT NULL,
        stars INT DEFAULT 0
    );""",

    "build_check_results": """
    CREATE TABLE IF NOT EXISTS build_check_results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        file_or_repo VARCHAR(255) NOT NULL UNIQUE,
        status TEXT
    );""",
    # updated_requirements TEXT
    # FOREIGN KEY (file_or_repo) REFERENCES papers(repo_url)

    "issues_classified": """
    CREATE TABLE IF NOT EXISTS issues_classified (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        body TEXT,
        labels VARCHAR(1000) DEFAULT NULL,
        comments_count INT DEFAULT 0,
        state VARCHAR(255) DEFAULT 'open',
        is_version_issue BOOLEAN DEFAULT FALSE
    );""",

    "updated_requirements": """
    CREATE TABLE IF NOT EXISTS updated_requirements (
        id INT AUTO_INCREMENT PRIMARY KEY,
        github_url VARCHAR(255) NOT NULL,
        updated_requirements MEDIUMTEXT
    );"""
    # FOREIGN KEY (github_url) REFERENCES papers(repo_url)
}


class Table:
    def __init__(self, table_name: str, db_name: str = "grimrepor_db"):
        self.table_name = table_name
        self.db_name = db_name
        # database has to work before creating tables
        # create_db(db_name=db_name)

    # def create_table_broken(self, create_table_cmd: str) -> bool:
    #     """
    #     create a table in the database
    #     note that in create session, the database is selected
    #     """
    #     session, schema = create_session(self.db_name)
    #     if not session: return False

    #     output = schema.get_table(self.table_name)
    #     if output:
    #         print(f"Table {self.table_name} already exists.{output.get_name() = }\n")
    #         return True

    #     try:
    #         session.sql(create_table_cmd).execute()
    #         print(f"Table {self.table_name} created successfully.")
    #         return True
    #     except Exception as e:
    #         print(f"Error creating table: {str(e)}")
    #         return False
    #     finally:
    #         session.close()

    def create_table(self, create_table_cmd: str) -> bool:
        """
        create a table in the database
        note that in create session, the database is selected
        """
        session, schema = create_session(self.db_name)
        if not session:
            return False

        try:
            # Check if the table exists
            table_exists = False
            tables = schema.get_tables()
            for table in tables:
                if table.get_name().lower() == self.table_name.lower():
                    table_exists = True
                    break

            if table_exists:
                print(f"Table {self.table_name} already exists.")
                return True

            # Create the table if it does not exist
            session.sql(create_table_cmd).execute()
            print(f"Table {self.table_name} created successfully.")
            return True
        except Exception as e:
            print(f"Error creating table: {str(e)}")
            return False
        finally:
            session.close()

    def populate_table_papers_and_code_linked(self) -> bool:
        """
        populate the table with data from data/links-between-papers-and-code.json
        sample:
        {
            "paper_url": "https://paperswithcode.com/paper/attngan-fine-grained-text-to-image-generation",
            "paper_title": "AttnGAN: Fine-Grained Text to Image Generation with Attentional Generative Adversarial Networks",
            "paper_arxiv_id": "1711.10485",
            "paper_url_abs": "http://arxiv.org/abs/1711.10485v1",
            "paper_url_pdf": "http://arxiv.org/pdf/1711.10485v1.pdf",
            "repo_url": "https://github.com/bprabhakar/text-to-image",
            "is_official": false,
            "mentioned_in_paper": false,
            "mentioned_in_github": false,
            "framework": "pytorch"
        },

        Not all rows are inserted due to unique and not null constraints
        clashes mainly on paper_url, paper_arxiv_id
        Rows inserted: 185013 of 272525
        """
        session, schema = create_session(self.db_name)
        if not session: return False

        columns = [
            "paper_url",
            "paper_title",
            "paper_arxiv_id",
            "paper_url_abs",
            "paper_url_pdf",
            "repo_url",
            "is_official",
            "mentioned_in_paper",
            "mentioned_in_github",
            "framework"
        ]

        rows_inserted = 0
        file_loc = os.path.join(ROOT, "data", "links-between-papers-and-code.json")
        data = None
        with open(file_loc, 'r', encoding='ascii') as f:
            data = json.load(f)

        table = schema.get_table(self.table_name)

        try:
            for idx, row in enumerate(data):
                row_values = [str(row.get(col, "")) for col in columns]
                # boolean tinyint(1) type; set true = 1, false = 0 to fit the schema
                for i in range(6, 9):
                    if row_values[i].lower() == "true":
                        row_values[i] = 1
                    elif row_values[i].lower() == "false":
                        row_values[i] = 0
                try:
                    schema.get_table(self.table_name).insert(columns).values(row_values).execute()
                    table.insert(columns).values(row_values).execute()
                    rows_inserted += 1
                except Exception as e:
                    print(f"Error inserting row #{idx}: {str(e)}")
                    continue
                print("{*}" * 120, f"\nrows parsed: {idx}\n", "{*}" * 120)

            print(f"Rows inserted: {rows_inserted} of attempted {len(data)}")
            print(f"Total rows: {table.count()}")

        except Exception as e:
            print(f"Error populating table: {str(e)}")
            return False
        finally:
            session.close()
        return True

    def populate_table_paper_repo_info_reqs(self) -> bool:
        r"""
        populate the table with data from data/paper_repo_info+reqs.json

        sample:
        ```
        {
            "paper_title": "AttnGAN: Fine-Grained Text to Image Generation with Attentional Generative Adversarial Networks",
            "paper_url": "https://paperswithcode.com/paper/attngan-fine-grained-text-to-image-generation",
            "paper_arxiv_id": "1711.10485",
            "repo_url": "https://github.com/bprabhakar/text-to-image",
            "is_official": "false",
            "framework": "pytorch",
            "readmeUrl": "https://raw.githubusercontent.com/bprabhakar/text-to-image/master/README.md",
            "requirementsUrl": "https://raw.githubusercontent.com/bprabhakar/text-to-image/master/requirements.txt",
            "requirementsLastCommitDate": "2018-05-30T01:01:19Z",
            "mostProminentLanguage": "Jupyter Notebook",
            "stars": "17",
            "lastCommitDate": "2018-05-30T01:28:48Z",
            "contributors": "https://github.com/bprabhakar",
            "requirements": "Flask\npython-dateutil\neasydict\nscikit-image\nazure-storage-blob\napplicationinsights\nlibmc"
        }
        ```
        """

        session, schema = create_session(self.db_name)
        if not session: return False

        # Define the mapping between JSON keys (camelCase) and database columns (snake_case)
        key_mapping = {
            "paper_title": "paper_title",
            "paper_url": "paper_url",
            "paper_arxiv_id": "paper_arxiv_id",
            "repo_url": "repo_url",
            "is_official": "is_official",
            "framework": "framework",
            "readmeUrl": "readme_url",
            "requirementsUrl": "requirements_url",
            "requirementsLastCommitDate": "requirements_last_commit_date",
            "mostProminentLanguage": "most_prominent_language",
            "stars": "stars",
            "lastCommitDate": "last_commit_date",
            "contributors": "contributors",
            "requirements": "requirements"
        }

        columns = [
            "paper_title",
            "paper_url",
            "paper_arxiv_id",
            "repo_url",
            "is_official",
            "framework",
            "readme_url",
            "requirements_url",
            "requirements_last_commit_date",
            "most_prominent_language",
            "stars",
            "last_commit_date",
            "contributors",
            "requirements"
        ]

        # Function to convert JSON keys to database column names
        def convert_keys(row, key_mapping):
            converted_row = {}
            for json_key, db_key in key_mapping.items():
                if json_key in row:
                    converted_row[db_key] = row[json_key]
                else:
                    converted_row[db_key] = None
            return converted_row


        rows_inserted = 0
        file_loc = os.path.join(ROOT, "data", "paper_repo_info+reqs.json")
        data = None
        # with open(file_loc, 'r', encoding='utf-8') as f:
        with open(file_loc, 'r', encoding='utf-8') as f:
            data = json.load(f)

        table = schema.get_table(self.table_name)

        # there may be empty columns
        try:
            for idx, row in enumerate(data):
                # Convert JSON keys to database column names
                field_dict = convert_keys(row, key_mapping)
                # prepare data to conform to the schema
                row_values = []

                for col in columns:
                    if col.lower().endswith("date"):
                        try:
                            date_value = datetime.strptime(field_dict[col], "%Y-%m-%dT%H:%M:%SZ").date()
                            row_values.append(date_value.strftime("%Y-%m-%d"))  # Convert date to string
                        except (ValueError, TypeError):
                            row_values.append(None)
                    elif col == "is_official":
                        row_values.append(1 if field_dict[col] == "true" else 0)
                    elif col == "stars":
                        row_values.append(int(field_dict[col]) if field_dict[col] is not None else 0)
                    else:
                        row_values.append(field_dict[col])

                # Insert the row into the database
                try:
                    table.insert(columns).values(row_values).execute()
                    rows_inserted += 1
                except Exception as e:
                    print(f"Error inserting row #{idx}: {str(e)}")
                    continue

            print(f"Rows inserted: {rows_inserted} of attempted {len(data)}")
            print(f"Total rows: {table.count()}")

        except Exception as e:
            print(f"Error populating table: {str(e)}")
            # return False
        finally:
            session.close()
        return True

    def populate_table_papers_data(self) -> bool:
        """
        populate the table with data from data/papers_data.json
        in csv format so it can be read as a dataframe
        or converted to json

        sample:
        ```
        Title                Sapiens: Foundation for Human Vision Models
        Link           https://paperswithcode.com/paper/sapiens-found...
        Author Info            facebookresearch/sapiens •  • 22 Aug 2024
        Abstract       We present Sapiens, a family of models for fou...
        Tasks                        2D Pose Estimation|Depth Estimation
        GitHub Link          https://github.com/facebookresearch/sapiens
        Star Count                                                 3,686
        """
        session, schema = create_session(self.db_name)
        if not session: return False

        columns = [
            "title", "paper_url", "author_info", "abstract", "tasks", "github_url", "stars"
        ]

        rows_inserted = 0
        file_loc = os.path.join(ROOT, "data", "papers_data.csv")

        data = None
        with open(file_loc, 'r', encoding='utf-8') as f:
            data = pd.read_csv(f)

        table = schema.get_table(self.table_name)

        try:
            for idx, row in data.iterrows():
                row = row.to_dict()
                for k, v in row.items():
                    # convert NaN to None
                    if pd.isna(v):
                        row[k] = None
                    # strip leading/trailing whitespace if the value is a string
                    elif isinstance(v, str):
                        row[k] = v.strip()
                    # remove commas from star count and convert to int
                    if k == "Star Count":
                        if row[k] is None or row[k] == "None" or row[k] == "":
                            row[k] = 0
                        else:
                            row[k] = int(row[k].replace(",", ""))
                try:
                    # print(f'Inserting row #{idx}: {list(row.values())}')
                    table.insert(columns).values(list(row.values())).execute()
                    rows_inserted += 1
                except Exception as e:
                    print(f"Error inserting row #{idx}: {str(e)}")
                    continue

            print(f"Rows inserted: {rows_inserted} of attempted {len(data)}")
            print(f"Total rows in table: {table.count()}")

        except Exception as e:
            print(f"Error populating table: {str(e)}")
            return False
        finally:
            session.close()
        return True

    def populate_table_build_check_results(self) -> bool:
        """
        populate the table with data from output/build_check_results.csv
        only has 'file_or_repo', 'status' fields
        sample:
        github_link	updated_requirements
        https://github.com/Maymaher/StackGANv2
        "torch==1.0.0 torchvision==0.2.1 numpy==1.15.1 lmdb==0.94
            easydict==1.9 six==1.11.0 requests==2.19.1 pandas==0.23.4
            Pillow==5.4.1 python_dateutil==2.7.5 tensorboardX==1.6
            PyYAML==3.13"
        """
        session, schema = create_session(self.db_name)
        if not session: return False

        columns = ["file_or_repo", "status"]

        rows_total = 0
        file_loc = os.path.join(ROOT, "output", "build_check_results.csv")

        data = None
        with open(file_loc, 'r', encoding='utf-8') as f:
            # data = json.load(f)
            data = pd.read_csv(f)

        table = schema.get_table(self.table_name)

        try:
            for idx, row in data.iterrows():
                row = row.to_dict()
                file_or_repo, status = None, 'open'

                for k, v in row.items():
                    if k == "file_or_repo":
                        file_or_repo = v.strip()
                    elif k == "status":
                        status = v.strip()

                try:
                    table.insert(columns).values([file_or_repo, status]).execute()
                    rows_total += 1
                except Exception as e:
                    print(f"Error inserting row #{idx}: {str(e)}")
                    continue

            print(f"Rows inserted: {rows_total} of attempted {len(data)}")
            print(f"Total rows: {table.count()}")

        except Exception as e:
            print(f"Error populating table: {str(e)}")
            return False
        finally:
            session.close()
        return True

    def populate_table_issues_classified(self) -> bool:
        """
        populate the table with data from output/issues_classified.csv
        only has 'title', 'body' fields
        """
        session, schema = create_session(self.db_name)
        if not session: return False

        # columns = ["title", "body", "labels", "comments_count", "state", "is_version_issue"]

        columns = ["title", "body"]

        rows_inserted = 0
        file_loc = os.path.join(ROOT, "output", "issues_classified.csv")
        data = None
        with open(file_loc, 'r', encoding='utf-8') as f:
            data = pd.read_csv(f)

        table = schema.get_table(self.table_name)

        try:
            for idx, row in data.iterrows():
                row = row.to_dict()
                title, body = None, None
                try:
                    title = row["title"]
                except KeyError:
                    pass
                try:
                    body = row["body"]
                except KeyError:
                    pass

                try:
                    table.insert(columns).values([title, body]).execute()
                    rows_inserted += 1
                except Exception as e:
                    print(f"Error inserting row #{idx}: {str(e)}")
                    continue

            print(f"Rows inserted: {rows_inserted} of attempted {len(data)}")
            print(f"Total rows: {table.count()}")

        except Exception as e:
            print(f"Error populating table: {str(e)}")
            return False
        finally:
            session.close()
        return True

    def populate_table_updated_requirements(self) -> bool:
        """
        populate the table with data from output/updated_requirements_results.csv
        only has 'github_link', 'updated_requirements' fields
        """
        session, schema = create_session(self.db_name)
        if not session: return False

        columns = ["github_url", "updated_requirements"]

        rows_inserted = 0
        file_loc = os.path.join(ROOT, "output", "updated_requirements_results.csv")
        data = None
        with open(file_loc, 'r', encoding='ascii') as f:
            data = pd.read_csv(f)

        table = schema.get_table(self.table_name)

        try:
            for idx, row in data.iterrows():
                row = row.to_dict()
                github_url, updated_requirements = None, 'No requirements found'

                for k, v in row.items():
                    if k == "github_link":
                        github_url = v.strip()
                    elif k == "updated_requirements":
                        updated_requirements = v.strip()

                try:
                    table.insert(columns).values([github_url, updated_requirements]).execute()
                    rows_inserted += 1
                except Exception as e:
                    print(f"Error inserting row #{idx}: {str(e)}")
                    continue

            print(f"Rows inserted: {rows_inserted} of attempted {len(data)}")
            print(f"Total rows: {table.count()}")

        except Exception as e:
            print(f"Error populating table: {str(e)}")
            return False
        finally:
            session.close()
        return True


if __name__ == '__main__':

    spinup_mysql_server()
    show_databases()
    create_db(db_name="grimrepor_db") # do once
    show_all_tables(db_name="grimrepor_db")
    # added user confirmation to drop all tables sa this is a destructive operation
    drop_all_tables(db_name="grimrepor_db")

    paper_repo_info_reqs = Table(table_name="paper_repo_info_reqs", db_name="grimrepor_db")
    paper_repo_info_reqs.create_table(create_table_dict["paper_repo_info_reqs"])
    show_table_columns("paper_repo_info_reqs", "grimrepor_db")
    paper_repo_info_reqs.populate_table_paper_repo_info_reqs()
    show_table_contents("paper_repo_info_reqs", "grimrepor_db", limit_num=10)

    papers_data = Table(table_name="papers_data", db_name="grimrepor_db")
    papers_data.create_table(create_table_dict["papers_data"])
    show_table_columns("papers_data", "grimrepor_db")
    papers_data.populate_table_papers_data()
    show_table_contents("papers_data", "grimrepor_db", limit_num=10)

    build_check_results = Table(table_name="build_check_results", db_name="grimrepor_db")
    build_check_results.create_table(create_table_dict["build_check_results"])
    show_table_columns("build_check_results", "grimrepor_db")
    build_check_results.populate_table_build_check_results()
    show_table_contents("build_check_results", "grimrepor_db", limit_num=10)

    papers_and_code_linked = Table(table_name="papers_and_code_linked", db_name="grimrepor_db")
    # print(f'{create_table_dict["papers_and_code_linked"] = }')
    papers_and_code_linked.create_table(create_table_dict["papers_and_code_linked"])
    show_table_columns("papers_and_code_linked", "grimrepor_db")
    # # Caution: large file, takes a few min
    # TODO: optimize speed
    papers_and_code_linked.populate_table_papers_and_code_linked()
    # DESIGN CHOICE: there are some papers with 10+ repos for example,
    # so consider if we want to link duplicates, have a separate table for duplicates,
    # keep track of which paper title corresponds and then delete all entries related after bulk upload
    show_table_contents("papers_and_code_linked", "grimrepor_db", limit_num=10)

    issues_classified = Table(table_name="issues_classified", db_name="grimrepor_db")
    issues_classified.create_table(create_table_dict["issues_classified"])
    show_table_columns("issues_classified", "grimrepor_db")
    issues_classified.populate_table_issues_classified()
    show_table_contents("issues_classified", "grimrepor_db", limit_num=10)

    updated_requirements = Table(table_name="updated_requirements", db_name="grimrepor_db")
    updated_requirements.create_table(create_table_dict["updated_requirements"])
    show_table_columns("updated_requirements", "grimrepor_db")
    updated_requirements.populate_table_updated_requirements()
    show_table_contents("updated_requirements", "grimrepor_db", limit_num=10)

    show_all_tables("grimrepor_db")

    # TODO: add foreign keys to the tables now that parsing works - come up with a schema for the database

# use a .env file at the root of the project with the following:
# MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD
