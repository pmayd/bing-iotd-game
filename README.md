# Where on Earth is this?

This little game is about guessing where the Bing daily photo was taken from. 

## Get running

```Bash
$ conda create -n flask python=3.9
$ conda activate flask
$ pip install --upgrade -r requirements.txt
$ flask run
```

## Database

The database is a json file that will be created in the root directory.

The database stores the users and their scores and the daily challenges.