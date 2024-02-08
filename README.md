# Receipt Challenge Fetch

## Problem Statement from Fetch

Hello!

This challenge utilizes Flask, Python, and Redis. Below are the Docker files provided. Ensure Docker is installed on your system.

##redis-pre-requisites:
brew install redis.
redis-start


receipt-challenge-fetch/
└── receipt-challenge/
    ├── backend/
    │   ├── app.py
    │   └── unit-tests.py
    └── docker-compose.yml

## files inside
programming logic is in app.py ,unit-tests.py are also added

## Cloning the Repository

After cloning the repository, follow the steps below:

## Docker Files Execution

1. Navigate to `receipt-challenge-fetch/receipt-challenge/backend`.
2. Execute the command: `sudo docker-compose build`.
3. Navigate to `receipt-challenge-fetch/receipt-challenge/`.
4. Execute the command: `sudo docker-compose up`.

## Accessing the URL

The URL is running at:

[http://127.0.0.1:8001/receipts/process](http://127.0.0.1:8001/receipts/process)
