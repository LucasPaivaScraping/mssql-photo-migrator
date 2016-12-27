# mssql-photo-migrator


## Dependencies (tested on Ubuntu 16.04 LTS) 

```bash
$ sudo apt-get install freetds-dev
```


## Installation

```bash
$ git clone https://github.com/kumbier/mssql-photo-migrator.git

$ cd mssql-photo-migrator/

$ sudo pip3 install -r requirements.txt
```

Set the DB parameters and the query to be used in `main.py`.


## Usage

```bash
python3 main.py
```


## Output

The images are stored in the project dir, by default in the "images" folder.
