# MAINTAINER: shane.harrell@signalwire.com
FROM debian:bullseye-slim

EXPOSE 8080

# Build argument to specify which agent file to use
ARG AGENT_TYPE=advanced

# Install basic packages
RUN apt update && apt install -y \
    curl \
    lsb-release \
    jq \ 
    nano \ 
    less


#  create app directory
RUN mkdir -p /app

# copy app files
COPY .env /app/.env
COPY app.py /app/app.py
COPY atom_agent-advanced.py /app/atom_agent-advanced.py
COPY atom_agent-simple.py /app/atom_agent-simple.py
# Copy the specified agent as the main agent file
COPY atom_agent-${AGENT_TYPE}.py /app/atom_agent.py
COPY templates /app/templates
COPY static /app/static
COPY requirements.txt /app/requirements.txt
COPY resource.py /app/resource.py
COPY start_services.sh /start_services.sh

# Install python and python dependencies
RUN apt update && apt install -y python3 python3-pip python3-venv

# Install NGROK
RUN apt-key adv --fetch-keys https://ngrok-agent.s3.amazonaws.com/ngrok.asc && echo "deb [arch=$(dpkg --print-architecture)] https://ngrok-agent.s3.amazonaws.com $(lsb_release -cs) main" |  tee /etc/apt/sources.list.d/ngrok.list && \
    apt update && apt install -y ngrok 

# Make start_services.sh executable
RUN chmod +x /start_services.sh

# Set the entrypoint to the start_services.sh script
ENTRYPOINT /start_services.sh
