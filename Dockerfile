# ---- Étape 1: Builder ----
# Installe toutes les dépendances, y compris les devDependencies pour les tests, etc.
FROM node:18-bullseye-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install

# Copie le reste du code source
COPY . .
# Si le projet avait une étape de build (ex: TypeScript -> JavaScript), elle irait ici.
# RUN npm run build

# ---- Étape 2: Production Dependencies ----
# Crée une installation propre avec uniquement les dépendances de production.
FROM node:18-bullseye-slim AS dependencies
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev

# ---- Étape 3: Production ----
# L'image finale, minimale et sécurisée.
FROM node:18-bullseye-slim
ENV NODE_ENV=production

# Crée un utilisateur non-root pour exécuter l'application
USER node

WORKDIR /app

# Copie les dépendances de production de l'étape 'dependencies'
COPY --from=dependencies --chown=node:node /app/node_modules ./node_modules
# Copie le code de l'application
COPY --chown=node:node . .

EXPOSE 3000
CMD ["node", "app.js"]