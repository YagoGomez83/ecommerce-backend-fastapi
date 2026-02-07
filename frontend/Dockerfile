# Dockerfile para Frontend (Desarrollo)
# Usa Node.js 20 Alpine (ligero y rápido)
FROM node:20-alpine

# Establece el directorio de trabajo
WORKDIR /app

# Copia package.json y package-lock.json (si existe)
COPY package*.json ./

# Instala las dependencias
RUN npm install

# Copia el resto del código
COPY . .

# Expone el puerto de Vite
EXPOSE 5173

# Comando para iniciar el servidor de desarrollo con hot-reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
