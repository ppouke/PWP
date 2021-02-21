# PWP SPRING 2020
# BlokusTrigonWeb
# Group information
* Student 1. Elmeri Uotila roope.uotila@student.oulu.fi
* Student 2. Juho Kalliokoski jkalliok@student.oulu.fi
* Student 3. Sakaria Pouke  ppouke@student.oulu.fi

# Project Description
Blokus Trigon playable on a browser. Uses Python Flask.

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

Dependencies: Found in requirements_TEsb4w3.txt

Database used: SQlite Version 2.6.0

# How to setup and populate database

Firstly, it is recommended initialize a new database/update the existing database to ensure the newest database schema is used.

The database can be initialized using python with:
```python
from app import db, State, Game, Player
db.create_all(()
```

Model instances can be created/edited/removed with SQLAlchemy procedures.

E.g. Creating and removing a Game instance with State and Player:
```python
#Create model instances

player = Player(color = "#CD5C5C")
state = State(placed_blocks = "0")
game = Game()

#Add relationships
game.board_state = state
game.players.append(player)

#Add and commit to database
db.session.add(player)
db.session.add(state)
db.session.add(game)

db.session.commit()
```

The diagram for relationships between models can be found in the wiki under DL2. Database design and implementation
  

# How to run tests of the database 
  On the command line in the ".../blokus/" directory simply run: 
  ```console 
  pytest
  ```
  
  The test_database.py file should be detected automatically
  
  Note. requires pytest installed with:
  ```console
  pip install pytest
  ```
  

