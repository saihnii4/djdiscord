FROM python:3

ADD test /
ADD commands /
ADD utils /

COPY bot.py /
COPY Pipfile /
COPY Pipfile.lock /
COPY views.csv /

# https://github.com/pypa/pipenv/issues/4273
RUN pip install 'pipenv'
RUN pipenv install --deploy --ignore-pipfile

ENTRYPOINT ["pipenv", "run", "python", "./bot.py"]

ENV WORKON_HOME /root

# Tells pipenv to use this specific Pipfile rather than the Pipfile in the 
# current working directory (the working directory changes between `docker build` 
# and `docker run`, this ensures we always use the same Pipfile)
ENV PIPENV_PIPFILE /Pipfile
