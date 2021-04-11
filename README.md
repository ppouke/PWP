# PWP SPRING 2021
# BlokusTrigonWeb
# Group information
* Student 1. Elmeri Uotila ruotila@student.oulu.fi
* Student 2. Juho Kalliokoski jkalliok@student.oulu.fi
* Student 3. Sakaria Pouke  ppouke@student.oulu.fi

# Project Description
Blokus Trigon playable on a browser. Uses Python Flask.

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

Dependencies: Found in requirements_TEsb4w3.txt

Database used: SQlite Version 2.6.0

# How to setup and populate database
The code for the database and testing is found under the /blokus/ directory

Firstly, it is recommended to initialize a new database/update the existing database to ensure the newest database schema is used.

The database can be initialized using python with:
```python
from app import db, State, Game, Player
db.create_all(()
```

Model instances can be created/edited/removed with SQLAlchemy procedures.

E.g. Creating a Game instance with State and Player:
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

The diagram for the relationships between models can be found in the wiki under DL2. Database design and implementation
  

# How to run tests of the database 
  On the command line in the ".../tests" directory simply run: 
  ```console 
  pytest --cov-report=term-missing --cov=blokus
  ```
  
  The test_database.py and resources_test.py file should be detected automatically
  
  The test_databse file tests the database with:
  1. Creating of instance models
  2. Finding instance in database and testing relationships
  3. Updating existing instances
  4. Removing instances
  5. Game - State one to one relationship errors
  6. Mandatory column errors
  7. testing ondelete funnctionality
  8. tests automatic generation of blocks
 
 The resources_test.py tests using requests on the implementation.
 Tests the following requests:
 
 Block Collection : GET, POST
 
 Block Item : GET, PUT, DELETE
 
 Game Collection : GET, POST
 
 Game Item : GET, POST, PUT, DELETE
 
 Player Item : GET
 
 Transaction Factory : GET, POST
 
 Transaction Items : GET, PUT, DELETE
 
 
  Note. requires pytest installed with:
  ```console
  pip install pytest
  ```
  

