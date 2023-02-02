# Readme

## Retro Games API

This is a school assignment using fastapi, pydantic, beanieODM, openapi, and mongoDB.

To run this project create a vierual environment and install the requirements.txt file.

```powershell
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
```
For password generation and the Mongodb connection to work you will need to create a .env file in the root directory with the following variables.

```
SALT=your_salt
MONGO_URI=your_mongo_uri
```

Finally, to run the project use the following command.

```powershell
uvicorn main:app --reload --port 8000
```
`main` is the name of the file and `app` is the name of the FastAPI instance.

Below is the assignment description.
___
### **Retro Video Game Exchange Rest API**
**Description:**

> Create a rest API that allows users to create an account and manage used retro video games that they wish to trade with other users  Anyone may register to use the video game exchange.  Once registered users may create video games in the system representing retro video game cartridges/disk that they own and wish to trade.  Other user's may search for specific video games and offer a trade.  The owner user has the option to accept or reject the trade.  If the trade is accepted ownership is transferred.

**Business Requirements**
> 1. Users may self register by providing at least their name, email address, and street address.
> 2. Once registered users create create, update, and delete records of their video games they are interested in trading.
> 3. A video game must store:  the name of the game, the publisher and year it was originally published, and the gaming system that plays the game.  A video must also have a condition (mint, good, fair, poor) and could optionally report how many owners it has had.
> 4. Any authenticated user may search for games, regardless of whether they have posted any of their own.
> 5. When a user finds a game they would like to obtain they can make an offer to trade some of their own games for the one they want.
> 6. An offer to trade is created in the API and is comprised of a list of games the offerer wishes to give and a list of games the offerer wishes to receive, as well as the user to which the trade is being offered (the current owner of the list of games the offerer wishes to receive).
> 7. In addition to the games and users, an offer should contain the date/time at which the offer was created as well as it's current state (pending, accepted, rejected).
> 8. A user should be able to retrieve a list of offers they have made and a list of offers they have received.  These lists should be able to be filtered by status (pending, accepted, rejected).
> 9. When an offer is accepted, the games included in the offer should change ownership appropriately.
> 10. Users may also update their own information including:  name and street address.  Their email address cannot be changed.
> 11. Users are required to create a password to use to access the service.  Users may change their own password at any time.
> 12. A user can reset their password by making a request to the service.  The service will generate a new temporary password and email it to the user.

### **Technical Requirements**
> 1. Your API should be defined and documented using OpenAPI
Your API must be Richardson Maturity Model level 3 (HATEOAS) compliant
> 2. Your API must use HTTP Basic authentication
> 3. Your API must use JSON as the primary data serialization mechanism.
> 4. Your persistent data storage can be in any relational database, graph database, or document database; columnar (column family) and key-value storage is not allowed on this assignment.
> 5. Your API should handle errors by responding with an appropriate (justifiable) HTTP response code and a json body with helpful information about the error.
### **Learning Objective**
> Students will gain practice in creating hypermedia compliant RMM level 3 restful APIs with persistent storage, authentication, and authorization.

### **Deliverables**
> Submit a zip file containing the source code for your project.
Pass off with the instructor or a coach, or reate a video recording of yourself explaining your code and demonstrating it's functionality using either prepared postman request or unit-tests in your framework. 