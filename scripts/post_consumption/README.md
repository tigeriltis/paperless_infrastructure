# Usage of the post_consume scripts

##  1.  In case of a docker installation of paperless

Put the scripts into subfolder `scripts` in the same folder as you keep the `docker-compose.yml`. This is a location that can be chosen arbitratily.

Mount the scripts folder into the container by creating the mount in `docker-compose.yml`:

    services:
      webserver:
        volumes:
          - ./scripts:/usr/src/paperless/scripts

Set the environment variable for the post consume script in `docker-compose.env` to run the script mounted into the container:

    PAPERLESS_POST_CONSUME_SCRIPT=/usr/src/paperless/scripts/post_consume_wrapper.sh

Restart the docker container to run with this updated configuration.
