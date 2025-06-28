# Base image
#FROM python:3.10

# Set work directory
#WORKDIR /app

# Set DNS to Google's public DNS to avoid resolution issues
#RUN echo "nameserver 8.8.8.8" >> /etc/resolv.conf

# Copy requirements file
#COPY requirements.txt .

# Install dependencies
#RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
#COPY . .

# Expose the port
#EXPOSE 8000

# Run migrations and start the server
#CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

FROM python:3.10

WORKDIR /app

# Update pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Copy and install dependencies with retry logic
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt --retries 5

# Copy project files
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the Django app with Gunicorn
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "messaging_app.wsgi:application"]
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
