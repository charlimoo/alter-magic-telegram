# Use an appropriate Python version
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary source files
COPY . .

# Make a directory for uploaded images 
RUN mkdir uploads

# Expose the desired port
EXPOSE 443

# Set the command to run your application
CMD ["python", "bot.py"]
