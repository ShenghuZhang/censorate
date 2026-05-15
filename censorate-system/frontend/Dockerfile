FROM node:22-alpine

WORKDIR /app

# Install system dependencies for node-gyp and other tools if needed
RUN apk add --no-cache libc6-compat

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start application in development mode
CMD ["npm", "run", "dev"]
