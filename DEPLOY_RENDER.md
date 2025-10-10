Deploying to Render (quick guide)

Render can build and run your Docker-based or buildpack-based web service. This project includes a `render.yaml` manifest that configures a web service and a managed Postgres database.

Steps
1. Push your code to a Git provider (GitHub/GitLab/Bitbucket) and connect the repo to Render.
2. Create a new Web Service on Render and point it to the repo (or import using `render.yaml`).
3. Set `DJANGO_SECRET_KEY` and any other secrets in Render's Environment -> Secrets.
4. Render will supply a `DATABASE_URL` for the managed Postgres. The application reads `DATABASE_URL` (via dj-database-url) to configure Django's `DATABASES` automatically.
5. Deploy and monitor the web service logs on Render.

Notes
- The `render.yaml` uses build and start commands appropriate for this Django app.
- We added `psycopg-binary` and `dj-database-url` to `requirements.txt` so Django can connect to Postgres provided by Render.
- Consider configuring a domain and SSL in Render settings when you move to production.
