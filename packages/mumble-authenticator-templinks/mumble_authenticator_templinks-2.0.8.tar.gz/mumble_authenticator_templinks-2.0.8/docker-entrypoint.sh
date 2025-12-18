#!/bin/sh -eux

# allow the container to be started with `--user`
if [ "$1" = 'authenticator' ] && [ "$(id -u)" = '0' ]; then
	find . \! -user app -exec chown app '{}' +
	exec gosu app "$0" "$@"
fi

exec "$@"
