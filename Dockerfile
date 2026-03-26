FROM python:3.9-slim
WORKDIR /modul1
COPY . /modul1
RUN pip install flask
EXPOSE 6767
CMD ["python", "modul1.py"]