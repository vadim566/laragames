From python:3.10
WORKDIR /LARA
ADD . /LARA
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python3.10","app.py"]