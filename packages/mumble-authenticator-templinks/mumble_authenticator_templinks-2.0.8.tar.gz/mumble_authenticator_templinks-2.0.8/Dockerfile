ARG DEBIAN_BASE_IMAGE=python:3.12-slim-trixie

# Build python package
FROM ${DEBIAN_BASE_IMAGE} AS build

ARG BUILD_DIR="/build"

WORKDIR ${BUILD_DIR}
COPY . ${BUILD_DIR}

ENV PATH="/root/.local/bin:$PATH"

RUN \
  set -eux; \
  pip install --no-color --disable-pip-version-check --no-cache-dir \
  uv \
  ; \
  uv build;

# Build runtime image
FROM ${DEBIAN_BASE_IMAGE} AS runtime

ARG APP_OWNER="app"
ARG APP_WORKDIR="/data"
ARG APP_UID=10000
ARG APP_GID=10000

ARG DEBIAN_FRONTEND=noninteractive
ARG DEBIAN_MIRROR="http://mirror.selectel.ru/debian"
ARG DEBIAN_SECURITY_MIRROR="http://mirror.selectel.ru/debian-security"

COPY --from=build /build/dist/*.whl /usr/src/
COPY docker-entrypoint.sh /

WORKDIR ${APP_WORKDIR}

RUN \
  set -eux; \
  apt_mirror() { \
  sed -i \
  -e "s|http://deb\.debian\.org/debian-security|$3|g" \
  -e "s|http://deb\.debian\.org/debian|$2|g" \
  $1; \
  }; \
  [ -w "/etc/apt/sources.list.d/debian.sources" ] && \
  apt_mirror "/etc/apt/sources.list.d/debian.sources" "${DEBIAN_MIRROR}" "${DEBIAN_SECURITY_MIRROR}"; \
  [ -w "/etc/apt/sources.list" ] && \
  apt_mirror "/etc/apt/sources.list" "${DEBIAN_MIRROR}" "${DEBIAN_SECURITY_MIRROR}"; \
  # Save current manually installed packages
  saved_apt_mark="$(apt-mark showmanual)"; \
  apt-get update; \
  # Install build dependencies
  apt-get install -y --no-install-recommends \
  build-essential \
  libbz2-dev \
  libssl-dev \
  ; \
  chmod +x /docker-entrypoint.sh; \
  addgroup --gid "${APP_GID}" "${APP_OWNER}"; \
  adduser --uid "${APP_UID}" --gid "${APP_GID}" --home "${APP_WORKDIR}" "${APP_OWNER}"; \
  chown "${APP_OWNER}:${APP_OWNER}" "${APP_WORKDIR}"; \
  pip install --no-color --disable-pip-version-check --no-cache-dir \
  /usr/src/*.whl \
  ; \
  # Restore apt-mark state
  apt-mark auto '.*' > /dev/null; \
  [ -z "$saved_apt_mark" ] || apt-mark manual $saved_apt_mark > /dev/null; \
  # Install runtime dependencies
  apt-get install -y --no-install-recommends \
  gosu \
  tini \
  ; \
  # Cleanup
  apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
  apt-get autoclean -y; \
  rm -rf \
  /var/cache/apt/archives/* \
  /var/lib/apt/lists/* \
  /var/log/alternatives.log \
  /var/log/apt* \
  /var/log/dpkg.log \
  ;

ENV MA__ICE_CLIENT__BIND_ADDRESS=0.0.0.0
ENV MA__ICE_CLIENT__PORT=13004
ENV MA__PROMETHEUS__ENABLED=true
ENV MA__PROMETHEUS__PORT=8000

EXPOSE ${MA__ICE_CLIENT__PORT}
EXPOSE ${MA__PROMETHEUS__PORT}

VOLUME ${APP_WORKDIR}

ENTRYPOINT ["tini", "--", "/docker-entrypoint.sh"]

CMD ["authenticator"]
