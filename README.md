# ApyHub changes in this branch

# HackThisFall-backend
Backend for Hack This Fall Season 3  - backend

First Create a Virtual Environment and activate it

To install virtualenv in Python
```
pip install virualenv
```

To create your virtual environment named "env" go to project directory and type the following command in terminal

```
 python<version> -m venv env
```

Activate the virtual environment, use the following command

```
source env/bin/activate or .env/Scripts/activate
```

To deactivate virtualenv simply use the command

```
deactivate
```

To install all the libraries required to run the project, use the following command

```
pip install -r requirements.txt
```

Then create a .env file in the project directory and paste the following code in it - 

```
database  = "mongodb+srv://kushal:kushalshah@hackthisfall3.magux9v.mongodb.net/?retryWrites=true&w=majority"

```


For database schema reference check schema.txt file

To run the backend application in local, the command is - 

```
python app.py
```