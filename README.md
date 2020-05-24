# Lyrics Finder

Finds all lyrics on metrolyrics and saves to PostgreSQL

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install required packages.

```bash
pip install -r requirements.txt
```

## Usage
For ```print_util.py``` to work properly [VSCode](https://code.visualstudio.com/) is recommended.

Now, you need to write your own credentials on ```db_operations.py ```

```python
def get_connection():
    conn = connect(database='', user='', password='',
                   host='', port='')
    return conn, conn.cursor()
```
Then simply just run:
```bash
python metrolyrics-crawler.py
```


## License
[MIT](https://choosealicense.com/licenses/mit/)