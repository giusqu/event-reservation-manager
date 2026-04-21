FROM python:3.13.6

COPY . .

RUN pip install -r requirements.txt

RUN chmod a+x deploy/*.sh # Give execution rights on deployment scripts