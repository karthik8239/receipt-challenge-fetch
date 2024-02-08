FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Create a virtual environment
RUN python3 -m venv .venv

# Activate the virtual environment
RUN /bin/bash -c "source .venv/bin/activate"

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Copy the rest of the application code into the container
EXPOSE 8001

# Define the command to start your Flask app
CMD ["python", "app.py"]


