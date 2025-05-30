# Step 1: Use Node.js base image
# FROM node:18.18.0
FROM node:22.16.0

# Set the working directory
WORKDIR /frontend

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 5173

# Command to run the frontend
CMD ["npm", "run", "dev"]
