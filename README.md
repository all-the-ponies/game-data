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

To use notifications, use `notifications-example.json` to create the notifications config. You can either place it in a `notifications.dev.json` file, or a `NOTIFICATIONS_CONFIG` environment variable. The github action expects a `NOTIFICATIONS_CONFIG` secret, so here's a quick command to put `notifications.prod.json` into that secret.

```shell
jq -c < notifications.prod.json | gh secret set NOTIFICATION_CONFIG
```

You need to get [ffdec](https://github.com/jindrapetrik/jpexs-decompiler/), and either add it to the path, or add `--ffdec ffdec.jar` to the command.

And of course to actually run it

```shell
uv run game-data --version latest --upload
```
