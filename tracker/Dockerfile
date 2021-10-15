FROM python:3.6
COPY requirements.txt .
RUN pip -q install -r requirements.txt

WORKDIR /user/local/bin/tracker
COPY . ./

# Set correct timezone in container
ENV TZ=America/Toronto
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENTRYPOINT [ "python", "-u" ]

CMD [ "main.py" ]
