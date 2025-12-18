#!/bin/sh -eux

poetry run \
	env \
	MA__DATABASE__NAME=alliance_auth \
	MA__DATABASE__USER=alliance_auth \
	MA__DATABASE__PASSWORD="supersecret" \
	MA__DATABASE__HOST=127.0.0.1 \
	MA__DATABASE__PORT=3307 \
	MA__DATABASE__PREFIX="" \
	MA__ICE_SERVER__HOST=127.0.0.1 \
	MA__ICE_SERVER__PORT=6502 \
	MA__ICE_SERVER__SECRET="supersecret" \
	MA__AVATAR__ENABLED=true \
	MA__AVATAR__CACHE_DIR="avatar_cache" \
	MA__AVATAR__CACHE_TTL=3600 \
	MA__ICE_PROPERTIES__0="Ice.ThreadPool.Server.Size=5" \
	MA__IDLEHANDLER__ENABLED=True \
	MA__LOG__LEVEL=debug \
	authenticator
