FROM python:3.6.10-buster

# Pull Image for Energyplus and install
# Collapse the update of packages, download and installation into one command
# to make the container smaller & remove a bunch of the auxiliary apps/files
# that are not needed in the container
RUN export DEBIAN_FRONTEND=noninteractive \
	&& apt-get update && apt-get install -y ca-certificates curl libasound2 libasound2-data vim \
    && rm -rf /var/lib/apt/lists/* \
    && curl -SLO https://github.com/NREL/EnergyPlus/releases/download/v8.9.0/EnergyPlus-8.9.0-40101eaafd-Linux-x86_64.sh \
    && chmod +x EnergyPlus-8.9.0-40101eaafd-Linux-x86_64.sh \
    && echo "y\r" | ./EnergyPlus-8.9.0-40101eaafd-Linux-x86_64.sh \
    && rm EnergyPlus-8.9.0-40101eaafd-Linux-x86_64.sh \
    && cd /usr/local/EnergyPlus-8-9-0 \
    && rm -rf DataSets Documentation ExampleFiles WeatherData MacroDataSets PostProcess/convertESOMTRpgm \
    PostProcess/EP-Compare PreProcess/FMUParser PreProcess/ParametricPreProcessor PreProcess/IDFVersionUpdater

# Remove the broken symlinks
RUN cd /usr/local/bin \
    && find -L . -type l -delete

# Install Java 
RUN apt update \
	&& apt install -y default-jre 

# Pull Image for BCVTB
RUN mkdir bcvtb \
	&& cd bcvtb\
	&& wget https://github.com/lbl-srg/bcvtb/releases/download/v1.6.0/bcvtb-install-linux64-v1.6.0.jar \
    && (echo "1"; sleep 1; echo "\r"; sleep 1; echo "\r"; sleep 1; echo "\r"; sleep 1; echo "1"; sleep 1; echo "/usr/local/bcvtb\r"; sleep 1; echo "1") | java -jar bcvtb-install-linux64-v1.6.0.jar \
    && cd .. \
    && mv /bcvtb /usr/local/bcvtb
    
# Creating a working directory and copy config and pip requirement files here 
VOLUME /var/uhc
WORKDIR /var/uhc
COPY . .

# Install Python packages requirements and then delete the file once done
RUN pip install -r requirements.txt \
	&& rm -f requirements.txt \

CMD [ "/bin/bash" ]
#CMD [ "python", "rl_main.py" ]
