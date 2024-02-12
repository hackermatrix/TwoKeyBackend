# Use an official Python runtime as a parent image
FROM python:3.9-buster

# Set the working directory to /backend
WORKDIR /backend

# Install system dependencies
RUN apt-get update \
    && apt-get install -y binutils libproj-dev gdal-bin \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .


# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /backend
COPY . .



RUN rm -rf fileoperations/migrations
RUN rm -rf logic/migrations
RUN rm -rf auth/migrations


RUN rm -rf fileoperations/__pycache__
RUN rm -rf logic/__pycache__
RUN rm -rf auth/__pycache__


# RUN python manage.py collectstatic --no-input

# RUN python manage.py migrate --fake

# Expose port 8000 for Django application
EXPOSE 8000
RUN chmod +x ./entrypoint.sh
# # Command to run your application
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
ENTRYPOINT [ "./entrypoint.sh" ]
