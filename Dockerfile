# Use an official Python runtime as a parent image
FROM python:alpine

# Set the working directory to /backend
WORKDIR /backend

# Copy the current directory contents into the container at /backend
COPY . .

# Install system dependencies
# RUN apt-get update \
#     && apt-get install -y binutils libproj-dev gdal-bin \
#     && rm -rf /var/lib/apt/lists/*

RUN apk update

RUN wget https://download.osgeo.org/gdal/3.8.3/gdal-3.8.3.tar.gz
RUN tar xzf gdal-3.8.3.tar.gz
RUN cd gdal-3.8.3
RUN ./configure
RUN make
RUN make install
RUN cd ..

# RUN echo "GDAL_LIBRARY_PATH = '/home/sue/local/lib/libgdal.so'"  >> ./backend/settings.py
# Create a virtual environment and activate it
RUN python -m venv venv
ENV PATH="/backend/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Make build.sh executable
# RUN chmod +x build.sh

# # Run the build.sh script
# RUN ./build.sh

RUN python manage.py migrate

# Expose port 8000 for Django application
EXPOSE 8000

# Command to run your application
CMD ["/backend/venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]
