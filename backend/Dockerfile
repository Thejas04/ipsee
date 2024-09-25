# Use Node.js 16 as the base image
FROM node:16

# Set the working directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the source code
COPY . .

# Expose port 3000 for the Node.js backend
EXPOSE 3000

# Start the Node.js app
CMD ["npm", "start"]
