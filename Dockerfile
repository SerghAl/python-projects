FROM python

WORKDIR /python_projects

COPY . .

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN export PATH="/root/.local/bin:$PATH"
RUN poetry install

CMD ["poetry", "run", "python", "main.py"]
EXPOSE 3000
