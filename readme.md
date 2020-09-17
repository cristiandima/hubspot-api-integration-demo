### Hubspot API Demo App

This is a small demo app which implements "Login with Hubspot" and syncs user deals to the database in the background. A simple table page displays this deal data.

Flask is used for the backend and mongodb and mongoengine for data storage.

### Project Setup

```
docker-compose up --build
```

Visit `http://localhost:3000` and click login with Hubspot. On login completion you get redirected to `http://localhost:3000/deals`. Refresh if deals not yet synced (takes a second or two for the first deals to show up).

### Models

Users
- get user id from hubspot, save to database, use session/cookie auth for subsequent calls

Assumption: we only interface with hotspot, use them as an auth service
Potential Refactoring: create our own user table, our own token, allow multiple social logins, etc

Deals
- sync deals from Hubspot in the background (on every sign in currently)
- sync command sent via rabbitmq to ensure job gets done eventually
Potential refactoring: Sync on a specific schedule, have a worker figure out when a sync is needed
