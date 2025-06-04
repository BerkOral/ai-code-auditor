FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    nodejs npm \
    php-cli php-xml \
    curl git unzip \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g eslint

RUN curl -sS https://getcomposer.org/installer | php && \
    mv composer.phar /usr/local/bin/composer

RUN composer global require phpstan/phpstan

ENV PATH="/root/.composer/vendor/bin:${PATH}"

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]

