FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y nodejs npm php php-cli php-xml git curl unzip && \
    npm install -g eslint && \
    curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer && \
    composer global require phpstan/phpstan

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV PATH="/root/.composer/vendor/bin:${PATH}"

EXPOSE 10000

CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
