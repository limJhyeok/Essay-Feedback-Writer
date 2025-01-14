# ChatGPT Clone Project - Development

## Docker Compose files and env vars

There is a main `docker-compose.yml` file with all the configurations that apply to the whole stack, it is used automatically by `docker compose`.

And there's also a `docker-compose.override.yml` with overrides for development, for example to mount the source code as a volume. It is used automatically by `docker compose` to apply overrides on top of `docker-compose.yml`.

These Docker Compose files use the `.env` file containing configurations to be injected as environment variables in the containers.

They also use some additional configurations taken from environment variables set in the scripts before calling the `docker compose` command.

## The .env file

The `.env` file is the one that contains all your configurations, generated keys and passwords, etc.

Depending on your workflow, you could want to exclude it from Git, for example if your project is public. In that case, you would have to make sure to set up a way for your CI tools to obtain it while building or deploying your project.

One way to do it could be to add each environment variable to your CI/CD system, and updating the `docker-compose.yml` file to read that specific env var instead of reading the `.env` file.

### Pre-commits and code linting

we are using a tool called [pre-commit](https://pre-commit.com/) for code linting and formatting.

When you install it, it runs right before making a commit in git. This way it ensures that the code is consistent and formatted even before it is committed.

You can find a file `.pre-commit-config.yaml` with configurations at the root of the project.

#### Install pre-commit to run automatically

`pre-commit` is already part of the dependencies of the project, but you could also install it globally if you prefer to, following [the official pre-commit docs](https://pre-commit.com/).

or if you have `apt` tool
```
apt install -y pre-commit
```


After having the `pre-commit` tool installed and available, you need to "install" it in the local repository, so that it runs automatically before each commit.


```bash
pre-commit install
```

Now whenever you try to commit, e.g. with:

```bash
git commit
```

...pre-commit will run and check and format the code you are about to commit, and will ask you to add that code (stage it) with git again before committing.

Then you can `git add` the modified/fixed files again and now you can commit.

#### Running pre-commit hooks manually

you can also run `pre-commit` manually on all the files, you can do it using Poetry with:

```bash
❯ pre-commit run

check for added large files..........................(no files to check)Skipped
check toml...........................................(no files to check)Skipped
check yaml...........................................(no files to check)Skipped
fix end of files.....................................(no files to check)Skipped
trim trailing whitespace.............................(no files to check)Skipped
ruff.................................................(no files to check)Skipped
ruff-format..........................................(no files to check)Skipped
```

## URLs

The production or staging URLs would use these same paths, but with your own domain.

### Development URLs

Development URLs, for local development.

Frontend: http://localhost:80

Backend: http://localhost/api/

Automatic Interactive Docs (Swagger UI): http://localhost/docs

Automatic Alternative Docs (ReDoc): http://localhost/redoc

Adminer: http://localhost:8080

Traefik UI: http://localhost:8090

### Development in localhost with a custom domain URLs

Development URLs, for local development.

Frontend: http://localhost.tiangolo.com

Backend: http://localhost.tiangolo.com/api/

Automatic Interactive Docs (Swagger UI): http://localhost.tiangolo.com/docs

Automatic Alternative Docs (ReDoc): http://localhost.tiangolo.com/redoc

Adminer: http://localhost.tiangolo.com:8080

Traefik UI: http://localhost.tiangolo.com:8090
