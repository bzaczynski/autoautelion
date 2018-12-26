# [autoautelion](http://autoautelion.herokuapp.com/)

Automated reporting of revenue and royalty fee for [Autelion](https://helion.pl/autelion/)-registered authors.

## Usage

TODO

These require authentication with configured credentials:

* Website: <http://autoautelion.herokuapp.com/>
* JSON API: <http://autoautelion.herokuapp.com/api>

## Development

Clone the repository from GitHub:

```shell
$ git clone git@github.com:bzaczynski/autoautelion.git
```

Make and activate virtual environment:

```shell
$ cd autoautelion
$ mkvirtualenv autoautelion
```

Install requirements:

```shell
$ pip install -r requirements.txt
```

Install local redis server:

```shell
$ sudo apt install redis-server
```

Export environment variables:

```shell
$ export AUTELION_USERNAME=<your-username>
$ export AUTELION_PASSWORD=<your-password>
$ export REDIS_URL=redis://localhost
$ export EMAIL_ADDRESS=<your-email>
$ export SENDGRID_API_KEY=<your-api-key>
```

Run updater job locally:

```shell
$ python updaterjob.py
```

Run web server locally:

```shell
$ FLASK_APP=webapp.py flask run
```

...alternatively:

```shell
$ gunicorn webapp:app
```

## Cloud Provisioning

Install Heroku command-line client:

```shell
$ sudo snap install heroku
```

Log in to your Heroku account, either via web browser:

```shell
$ heroku login
```

...or from the terminal:

```shell
$ heroku login -i
```

This will create and store a new session in `~/.netrc` file.

Change directory to the cloned GitHub repository:

```shell
$ cd autoautelion
```

If you had already created a Heroku app through their website, then add a Git remote with the corresponding app name, e.g.

```shell
$ heroku git:remote -a autoautelion
```

Otherwise, simply create a new app. If you omit the name a random one will be chosen automatically.

```shell
$ heroku create autoautelion
```

Install add-ons. Note this requires account verification by providing your credit card details to Heroku (for abuse prevention).

```shell
$ heroku addons:create heroku-redis:hobby-dev -a autoautelion
$ heroku addons:create scheduler:standard
$ heroku addons:create sendgrid:starter
```

This will take a while, so you may want to check the creation status:

```shell
$ heroku addons
```

Schedule a background job to run daily:

```shell
$ heroku addons:open scheduler
```

...then enter `python updaterjob.py` as the command.

Grab SendGrid auto-generated username and password:

```shell
$ heroku config | grep SENDGRID
```

Navigate your browser to <https://app.sendgrid.com/settings/api_keys> and log in using the obtained credentials. Click the `Create API Key` button, choose full access key and then provide key name e.g. `autoautelion`. Copy the key and define a Heroku environment variable. Note that SendGrid will not show the key again!

```shell
$ heroku config:set SENDGRID_API_KEY=<your-api-key>
```

Scale the web process:

```shell
$ heroku ps:scale web=1
```

### Configuration

To set or update remote configuration on Heroku:

```shell
$ heroku config:set AUTELION_USERNAME=<your-username> AUTELION_PASSWORD=<your-password>
$ heroku config:set SENDGRID_API_KEY=<your-api-key> EMAIL_ADDRESS=<your-email>
```

Note that `REDIS_URL` variable is configured automatically.

Confirm remote configuration validity. This will also display other environment variables, e.g. for add-ons:

```shell
$ heroku config
```

Changing configuration creates and deploys a new release. To see all releases:

```shell
$ heroku releases
```

### Releasing

If Heroku app has been connected to a GitHub account then pushing directly to origin `master` or accepting a pull request will trigger the build and deployment of a new release.

Otherwise use Heroku Git remote:

```shell
$ git push heroku master
```

To rollback a release to the immediately previous version:

```shell
$ heroku rollback
```

...or to a specific one:

```shell
$ heroku rollback v123
```

### Testing

To test locally:

```shell
$ heroku local
```

To open deployed app on Heroku:

```shell
$ heroku open
```

If something goes wrong, take a look at the logs:

```shell
$ heroku logs --tail
```

List dynos for the app:

```shell
$ heroku ps
```

Run a one-off dyno (temporary container) with `/bin/bash` to debug:

```shell
$ heroku run bash
```
