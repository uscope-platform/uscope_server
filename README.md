# uScope server

The server component of the uscope platform stack Implements the backend for the client web application. These are its main functions:

- Authentication: The server protects the mission critical components from unauthorized access through a standard authentication mechanism with username and password

- Role based authorization: Each user is associated to a role, with defined capabilities (application creation, script definition, etc.)

- Database management: The server manages the database implementing persistence for user generated data.

- Program compilation: The server compiles/assembles fCore programs through the fCore_has compiler module.