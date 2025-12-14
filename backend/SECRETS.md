# Secret Management

## Local Development

### Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values (defaults are fine for local dev):
   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=monday_merch
   SECRET_KEY=dev-secret-key
   ```

3. Run docker-compose:
   ```bash
   docker-compose up
   ```

**Note**: `.env` is already in `.gitignore` - never commit it.

## Production

### Option 1: Environment Variables (.env file)

1. Create `.env` on production server:
   ```bash
   # Generate secure secrets
   SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
   DB_PASSWORD=$(openssl rand -base64 32)

   # Create .env file
   cat > .env << EOF
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=$DB_PASSWORD
   POSTGRES_DB=monday_merch
   SECRET_KEY=$SECRET_KEY
   DEBUG=false
   EOF
   ```

2. Set file permissions:
   ```bash
   chmod 600 .env
   ```

3. Deploy:
   ```bash
   docker-compose up -d
   ```

### Option 2: Docker Secrets (Docker Swarm)

1. Initialize swarm:
   ```bash
   docker swarm init
   ```

2. Create secrets:
   ```bash
   echo "secure-db-password" | docker secret create postgres_password -
   echo "secure-secret-key" | docker secret create secret_key -
   ```

3. Update `docker-compose.yml`:
   ```yaml
   services:
     db:
       secrets:
         - postgres_password
       environment:
         POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password

     api:
       secrets:
         - secret_key
       environment:
         SECRET_KEY_FILE: /run/secrets/secret_key

   secrets:
     postgres_password:
       external: true
     secret_key:
       external: true
   ```

4. Deploy:
   ```bash
   docker stack deploy -c docker-compose.yml monday-merch
   ```

### Option 3: External Secret Manager (AWS Secrets Manager)

1. Store secrets:
   ```bash
   aws secretsmanager create-secret \
     --name prod/monday-merch/db-password \
     --secret-string "secure-password"

   aws secretsmanager create-secret \
     --name prod/monday-merch/secret-key \
     --secret-string "secure-secret-key"
   ```

2. Create startup script `start.sh`:
   ```bash
   #!/bin/bash
   export POSTGRES_PASSWORD=$(aws secretsmanager get-secret-value \
     --secret-id prod/monday-merch/db-password \
     --query SecretString --output text)

   export SECRET_KEY=$(aws secretsmanager get-secret-value \
     --secret-id prod/monday-merch/secret-key \
     --query SecretString --output text)

   docker-compose up -d
   ```

3. Run:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

### Option 4: Kubernetes Secrets

1. Create secret:
   ```bash
   kubectl create secret generic monday-merch-secrets \
     --from-literal=postgres-password='secure-password' \
     --from-literal=secret-key='secure-secret-key'
   ```

2. Reference in deployment:
   ```yaml
   env:
     - name: POSTGRES_PASSWORD
       valueFrom:
         secretKeyRef:
           name: monday-merch-secrets
           key: postgres-password
     - name: SECRET_KEY
       valueFrom:
         secretKeyRef:
           name: monday-merch-secrets
           key: secret-key
   ```

## Generating Secure Secrets

```bash
# SECRET_KEY (32+ characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"
# or
openssl rand -base64 32

# Database password (32+ characters)
openssl rand -base64 32
```

## Differences: Dev vs Prod

| Aspect | Development | Production |
|--------|-------------|------------|
| **Secrets Source** | `.env` file with defaults | Secret manager or secure `.env` |
| **Default Values** | OK to use (`postgres`, `dev-secret`) | Must be changed |
| **Password Strength** | Simple passwords OK | Strong random passwords (32+ chars) |
| **Secret Rotation** | Not required | Regular rotation recommended |
| **Access Control** | Local machine | Restricted access, audit logs |
| **Storage** | Local `.env` file | Encrypted secret store |
| **Port Exposure** | Expose ports for testing | Use internal networks only |
