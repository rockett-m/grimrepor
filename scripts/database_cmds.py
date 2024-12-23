import os
import sys
import subprocess
import argparse

from dotenv import load_dotenv

load_dotenv()
ROOT = subprocess.check_output("git rev-parse --show-toplevel", shell=True).decode('utf-8').strip()
OS = sys.platform
if OS != 'linux' and OS != 'darwin':
    raise Exception('Unsupported OS')

def parse_args():
    parser = argparse.ArgumentParser(description='Database commands')
    parser.add_argument('db_name', type=str, help='Name of the database')
    parser.add_argument('table_name', type=str, help='Name of the table')
    parser.add_argument('--paper_id', type=int, help='ID of the paper')
    parser.add_argument('--data', type=dict, help='Data to be added/updated in the table')
    args = parser.parse_args()
    return args

def install_mysql() -> bool:
    """
    choosing default installation (not secure)
    run mysql_secure_installation for secure installation
    """
    # if already installed, return
    cmd_test = ['mysql', '--version']

    if OS == 'linux':
        cmd_test.insert(0, 'sudo')
        result = subprocess.run(cmd_test)
        if result.returncode == 0:
            print("MySQL is already installed.")
            return True
        else:
            print("MySQL is not installed. Installing MySQL...")
            # install mysql if not installed and check status to verify
            try:
                subprocess.run(['sudo', 'apt', 'update'], check=True)
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
    if OS == 'linux':
        try:
            subprocess.run(['sudo', 'systemctl', 'start', 'mysql'], check=True)
            print("MySQL server started successfully on Linux.")
            return True
        except Exception as e:
            print(f"Error starting MySQL server on Linux: {str(e)}")
            return False
    elif OS == 'darwin':
        try:
            subprocess.run(['brew', 'services', 'start', 'mysql'], check=True)
            print("MySQL server started successfully on macOS.")
            return True
        except Exception as e:
            print(f"Error starting MySQL server on macOS: {str(e)}")
            return False
    else:
        print("Unsupported OS")
        return False

def run_mysql() -> bool:
    cmd = 'mysql;'
    if OS == 'linux':
        cmd = 'sudo ' + cmd
    try:
        subprocess.run([cmd])
        return True
    except Exception as e:
        print(f"Error launching mysql: {str(e)}")
        return False
    return False

def create_db(db_name: str) -> bool:
    """
    create a new database
    """
    # spin up mysql server
    if not launch_server():
        print("Error launching mysql server")
        return False
    # create database
    cmd_subprocess = ['mysql', '-e', f'CREATE DATABASE IF NOT EXISTS {db_name};']
    if OS == 'linux':
        cmd_subprocess.insert(0, 'sudo')
    try:
        subprocess.run(cmd_subprocess, check=True)
        return True
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        return False

def show_databases() -> bool:
    cmd_show_db = ['mysql', '-e', 'SHOW DATABASES;']
    if OS == 'linux':
        cmd_show_db.insert(0, 'sudo')
    try:
        subprocess.run(cmd_show_db, check=True)
        return True
    except Exception as e:
        print(f"Error showing databases: {str(e)}")
        return False

def create_table(db_name: str, table_name: str = "papers") -> bool:
    # TODO: make columns match the ones in the rest of our code
    # select the database
    cmd_select_db = ['mysql', '-e', f'USE {db_name};']
    if OS == 'linux':
        cmd_select_db.insert(0, 'sudo')
    try:
        subprocess.run(cmd_select_db, check=True)
    except Exception as e:
        print(f"Error selecting database: {str(e)}")
        return False

    cmd_table = ['mysql', '-e', f"""
    USE {db_name};
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255),
        author VARCHAR(255),
        year INT,
        github_url VARCHAR(255),
        arxiv_url VARCHAR(255),
        status VARCHAR(255),
        reqs_found BOOLEAN,
        reqs_fixed BOOLEAN,
        reqs_file_orig MEDIUMBLOB,
        reqs_file_fixed MEDIUMBLOB,
        notified BOOLEAN
    );"""]
    if OS == 'linux':
        cmd_table.insert(0, 'sudo')
    try:
        subprocess.run(cmd_table, check=True)
        return True
    except Exception as e:
        print(f"Error creating table: {str(e)}")
        return False

def show_table_columns(db_name: str, table_name: str) -> bool:
    cmd_show_columns = ['mysql', '-e', f"""
    USE {db_name};
    SHOW COLUMNS FROM {table_name};"""]

    if OS == 'linux':
        cmd_show_columns.insert(0, 'sudo')
    try:
        subprocess.run(cmd_show_columns, check=True)
        return True
    except Exception as e:
        print(f"Error showing table columns: {str(e)}")
        return False

def add_paper_to_table(db_name: str, table_name: str, data: dict) -> bool:
    # select the database
    cmd_select_db = f'USE {db_name};'
    if OS == 'linux':
        cmd_select_db = "sudo " + cmd_select_db
    try:
        subprocess.run(['mysql', '-e', cmd_select_db])
    except Exception as e:
        print(f"Error selecting database: {str(e)}")
        return False

    # add paper to the table
    cmd_add = ['mysql', '-e',
    f"""
    USE {db_name};
    INSERT INTO {table_name} (title, author, year, github_url, arxiv_url,
                        status, reqs_found, reqs_fixed,
                        reqs_file_orig, reqs_file_fixed, notified)
    VALUES ('{data['title']}', '{data['author']}', {data['year']}, '{data['github_url']}',
            '{data['arxiv_url']}', '{data['status']}', {data['reqs_found']}, {data['reqs_fixed']},
            {data['reqs_file_orig']}, {data['reqs_file_fixed']}, {data['notified']});
    """]
    # add prefix of sudo for linux
    if OS == 'linux':
        cmd_add.insert(0, 'sudo')
    try:
        subprocess.run(cmd_add, check=True)
        return True
    except Exception as e:
        print(f"Error adding paper to table: {str(e)}")
        return False

def update_paper_status(db_name: str, table_name: str, paper_id: int, data: dict) -> bool:
    # select the database
    cmd_select_db = ['mysql', '-e', f'USE {db_name};']
    if OS == 'linux':
        cmd_select_db.insert(0, 'sudo')
    try:
        subprocess.run(['mysql', '-e', cmd_select_db])
    except Exception as e:
        print(f"Error selecting database: {str(e)}")
        return False

    # update paper status
    cmd_update = ['mysql', '-e', f"""
    USE {db_name};
    UPDATE {table_name}
    SET reqs_found = {data['reqs_found']},
    reqs_fixed = {data['reqs_fixed']},
    notified = {data['notified']}
    WHERE id = {paper_id};
    """]
    # add prefix of sudo for linux
    if OS == 'linux':
        cmd_update.insert(0, 'sudo')

    try:
        subprocess.run(cmd_update, check=True)
        return True
    except Exception as e:
        print(f"Error updating paper status: {str(e)}")
        return False


def init_db_and_table(db_name: str = 'grimreaper_db', table_name: str = 'papers') -> bool:
    """
    produced this:
    MySQL server started successfully on macOS.
    +-----------------+--------------+------+-----+---------+----------------+
    | Field           | Type         | Null | Key | Default | Extra          |
    +-----------------+--------------+------+-----+---------+----------------+
    | id              | int          | NO   | PRI | NULL    | auto_increment |
    | title           | varchar(255) | YES  |     | NULL    |                |
    | author          | varchar(255) | YES  |     | NULL    |                |
    | year            | int          | YES  |     | NULL    |                |
    | github_url      | varchar(255) | YES  |     | NULL    |                |
    | arxiv_url       | varchar(255) | YES  |     | NULL    |                |
    | status          | varchar(255) | YES  |     | NULL    |                |
    | reqs_found      | tinyint(1)   | YES  |     | NULL    |                |
    | reqs_fixed      | tinyint(1)   | YES  |     | NULL    |                |
    | reqs_file_orig  | mediumblob   | YES  |     | NULL    |                |
    | reqs_file_fixed | mediumblob   | YES  |     | NULL    |                |
    | notified        | tinyint(1)   | YES  |     | NULL    |                |
    +-----------------+--------------+------+-----+---------+----------------+
    """

    # install mysql
    if not install_mysql():
        print("Error installing mysql")
        return False

    # create database
    if not create_db(db_name):
        print("Error creating database")
        return False

    # create table
    if not create_table(db_name, table_name):
        print("Error creating table")
        return False

    # show table columns
    if not show_table_columns(db_name, table_name):
        print("Error showing table columns")
        return False

    return True



if __name__ == '__main__':

    init_db_and_table()


    """ review later - will be best to import functions into another file and call them from there

    parser = argparse.ArgumentParser(description='Database commands')
    parser.add_argument('db_name', type=str, help='Name of the database')
    parser.add_argument('table_name', type=str, help='Name of the table')
    parser.add_argument('--paper_id', type=int, help='ID of the paper')
    parser.add_argument('--data', type=dict, help='Data to be added/updated in the table')
    args = parser.parse_args()

    # install mysql
    if not install_mysql():
        print("Error installing mysql")
        sys.exit(1)

    # create database
    if not create_db(args.db_name):
        print("Error creating database")
        sys.exit(1)

    # create table
    if not create_table(args.db_name, args.table_name):
        print("Error creating table")
        sys.exit(1)

    # show table columns
    if not show_table_columns(args.db_name, args.table_name):
        print("Error showing table columns")
        sys.exit(1)

    # add paper to table
    if args.data:
        if not add_paper_to_table(args.db_name, args.table_name, args.data):
            print("Error adding paper to table")
            sys.exit(1)

    # update paper status
    if args.paper_id and args.data:
        if not update_paper_status(args.db_name, args.table_name, args.paper_id, args.data):
            print("Error updating paper status")
            sys.exit(1)

    sys.exit(0)
    """


"""
reference commands for mysql

# install mysql
brew install mysql
# start server
brew services start mysql
# login to mysql server with root user and passwordless
mysql -u root;

# create and select database 'grimreaper_db'
SHOW DATABASES;
CREATE DATABASE grimreaper_db IF NOT EXISTS;
USE grimreaper_db;
SHOW DATABASES;

SHOW TABLES;
CREATE TABLE papers IF NOT EXISTS(
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(255),
    year INT,
    github_url VARCHAR(255),
    arxiv_url VARCHAR(255),
    status VARCHAR(255),
    reqs_found BOOLEAN,
    reqs_fixed BOOLEAN,
    reqs_file_orig MEDIUMBLOB,
    reqs_file_fixed MEDIUMBLOB,
    notified BOOLEAN
);
# check if columns are created
SHOW COLUMNS FROM papers;

# populate table as we get new papers
INSERT INTO papers (title, author, year, github_url, arxiv_url,
                    status, reqs_found, reqs_fixed,
                    reqs_file_orig, reqs_file_fixed, notified)
VALUES ('A paper on software engineering', 'John Doe', 2021, 'https://github.com/sundai-club/grimrepor",
        'https://arxiv.org/abs/1234.5678', 'pending', FALSE, FALSE, NULL, NULL, FALSE);

# show all papers in the table
SELECT * FROM papers;

# update a paper's status
UPDATE papers
SET reqs_found = TRUE,
reqs_fixed = TRUE.
notified = TRUE
WHERE id = 1;

"""