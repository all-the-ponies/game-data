# game-data

This script reads and transforms the mlp game data to be used for [All The Ponies](https://all-the-ponies.com/). The assets are uploaded to https://assets.all-the-ponies.com/, which is a Cloudflare R2 bucket. This script is not meant to be run without an s3-like bucket, and you do need some expertise to run anything (the below is mostly just for me to remember commands).

# Setup

If you want to run this yourself, you need a few things.

In a `.env` file, or just setting these environment variables, you can configure the S3-like bucket. Note: the script won't work without one.

```shell
S3_ENDPOINT=http://localhost:3000
S3_ACCESS_KEY=testing
S3_SECRET_KEY=testing
S3_REGION=us-east-1
```

To use notifications, use `notifications-example.json` to create the notifications config. Place it in either `notifications.dev.json` for running it in the dev environment, or `notifications.json` for production.

You need to get [ffdec](https://github.com/jindrapetrik/jpexs-decompiler/), and either add it to the path, or add `--ffdec ffdec.jar` to the command.

You also need to first install the `cairo` headers. Instructions can be found here: https://pycairo.readthedocs.io/en/latest/getting_started.html

And of course to actually run it

```shell
uv run game-data --version latest --upload
```

If all of this is too complicated, you can just use the docker container.

```shell
docker build -t game-data . 
docker run --env-file .env game-data
```


## Google Play API

This project uses the google play api to find updates as soon as possible, but that does require a google account which I do not provide. You are able to run the script without one though, as it also checks the google play website, it just may not find an update immediately.

The first time you run this, you need to have a token dispenser. See https://gitlab.com/AuroraOSS/aurora-dispenser to self-host.

Set these environment variables

```shell
export PLAYSTORE_DISPENSER_URL="https://example.com/api/auth" # REPLACE WITH YOUR URL
export PLAYSTORE_TOKEN='ya29.fooooo' # optional
export PLAYSTORE_GSFID='1234567891234567890' # optional
```

After the first run, the login config will be saved to `config/gplay.json`, **keep this file safe**.

Any subsequent runs don't need any environment variables as long as `config/gplay.json` exists.

Here are some additional environment variables you can set up for requests.

```shell
export HTTP_PROXY='http://localhost:8080'
export HTTPS_PROXY='http://localhost:8080'
export CURL_CA_BUNDLE='/usr/local/myproxy_info/cacert.pem'
```
