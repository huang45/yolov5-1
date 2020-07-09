FROM yolov5-base

# add recent pypi packages
RUN pip install huawei-lte-api==1.4.12 pytz==2020.1

# Create working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy repo contents
COPY . /usr/src/app

# Clean the weights and inference mountpoints, they must be mounted 
# at run-time
RUN rm -rf weights inference 


