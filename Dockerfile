FROM python:3.7

ADD circleci circleci
ADD requirements.txt requirements.txt
ADD main.py main.py

RUN echo "GITHUB_TOKEN=${GITHUB_TOKEN}"
RUN export GITHUB_TOKEN=${GITHUB_TOKEN}
RUN pip install pip --upgrade --progress-bar off
RUN pip install -r requirements.txt --progress-bar off
ENTRYPOINT ["python", "/main.py"]