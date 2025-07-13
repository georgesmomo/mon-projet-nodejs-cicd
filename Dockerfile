# Étape 1 : Build
FROM node:18-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Étape 2 : Runtime (non-root)
FROM node:18-alpine

# Crée un utilisateur non-root et groupe
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /usr/src/app

# Copie depuis l'étape build
COPY --from=build /app /usr/src/app

# Change le propriétaire des fichiers
RUN chown -R appuser:appgroup /usr/src/app

# Bascule sur l'utilisateur non-root
USER appuser

EXPOSE 3000
CMD ["node", "app.js"]
