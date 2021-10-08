FROM rabbitmq:3-management

# Define environment variables.
ENV RABBITMQ_PID_FILE /var/lib/rabbitmq/core/rabbitmq

ADD init.sh /init.sh
RUN chmod +x /init.sh
EXPOSE 5672
EXPOSE 15672

# Set correct timezone in container
ENV TZ=America/Toronto
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Define default command
CMD ["/init.sh"]
