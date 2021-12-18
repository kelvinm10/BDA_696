# PythonProject

# Setup for developement:

- Setup a python 3.x venv (usually in `.venv`)
  - You can run `./scripts/create-venv.sh` to generate one
- `pip3 install --upgrade pip`
- Install pip-tools `pip3 install pip-tools`
- Update dev requirements: `pip-compile --output-file=requirements.dev.txt requirements.dev.in`
- Update requirements: `pip-compile --output-file=requirements.txt requirements.in`
- Install dev requirements `pip3 install -r requirements.dev.txt`
- Install requirements `pip3 install -r requirements.txt`
- `pre-commit install`

## Update versions

`pip-compile --output-file=requirements.dev.txt requirements.dev.in --upgrade`

# Run `pre-commit` locally.

`pre-commit run --all-files`

## Final:

- docker-compose up will run the final code
- all results will be added to a "finalResults" folder
- Add the "baseball.sql" database file in the root of the project
- I had some last minute issues running bash scripts from my dockerfile, so I had to revert to adding a sleep funciton in my python code and running the sql scripts as initializaton files

## Midterm:

- main function takes in 3 parameters: pandas dataframe, list of predictor names (strings), and name of response (string)
- outputs a maximum of 6 files: "continuous_predictors_table.html" , "cat_cont_predictors_table.html" , "cat_predictors_table.html" , "cont_cont_brute_force_table.html" , "cont_cat_brute_force_table.html" , "cat_cat_brute_force_table.html"
- maximum of 3 correlation matrices will be automatically displayed in browser

## Assignment 4:

- main function takes in 3 parameters: pandas dataset, list of predictor names (strings), and name of response (string)
- outputs a "finalTable.html" file which can be opened on a browser and all information is in the table

## Assignment 5:

- The variable ranking and brute force tables are in the "finalTables" folder in the assignments folder
- the results of the random forest and logistic regression are printed out to the console

## Assignment 6:

- dockerfile and docker-compose file are in the root of the project.
- Assumes that database "baseball.sql" is in the root of the project (same directory level as docker files)
- running "docker-compose up" will create the 2 images and run all the code in assignment5.
- When running for the first time, it takes about 5-10 min for the baseball database to be imported and loaded into the mariadb instance, because of this there is a `sleep` function in assignment 5 just before executing the first sql command in order to allow for the connection to be live
- After the containers have already been built, the docker containers run much quicker
- All tables and results from the assignment5 python script are in the "finalResults" directory in the root of the project
