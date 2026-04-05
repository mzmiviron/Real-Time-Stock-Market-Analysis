FROM spark:3.5.1-python3

# Switch to root to install packages and create directories
USER root

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create ivy cache directory for spark user
RUN mkdir -p /home/spark/.ivy2 && chown -R spark:spark /home/spark/.ivy2

# Switch back to spark user
USER spark

# The consumer code will be mounted at runtime via volumes