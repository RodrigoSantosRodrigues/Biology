# API Rest Biology
Database for biological applications

## Installation
  - Install [Python](https://www.python.org/downloads/), [Pipenv](https://docs.pipenv.org/) or [Anaconda](https://www.anaconda.com/) and [Postgres](https://www.postgresql.org/) on your machine

  - Activate the project virtual environment with `$ pipenv shell` command or `conda activate myenv`
  - Install  `$ pipenv install` or Anaconda
  - Developed in anaconda environment
  - `install -r requirements.txt` to install dependencies
  - Export the required environment variables
      ```
      $ export FLASK_ENV=development
      $ export DATABASE_URL=postgres://name:password@houst:port/blog_api_db
      $ export JWT_SECRET_KEY=hhgaghhgsdhdhdd
      ```
  - Start the app with `python run.py`


## Compatibility
* [Tested on Python 2.7 and 3.6, 3.7]

Notes
=================
