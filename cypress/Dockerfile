FROM cypress/included:13.17.0

WORKDIR /e2e

COPY docker-entrypoint.sh /usr/local/bin/cypress-e2e-entrypoint.sh
RUN chmod +x /usr/local/bin/cypress-e2e-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/cypress-e2e-entrypoint.sh"]
