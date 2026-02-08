# deploy-app1

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/nikvladimirovich2/deploy-app1.git
cd deploy-app1
```

### 2. Configure Environment Variables

Edit or create `.env` file with your configuration:
Change default password.

### 3. Start the Application

```bash
python deployctl.py up
```

Expected output:
```
{"status": "Application deployed successfully"}
```

## Usage

### Deploy Application

```bash
python deployctl.py up
```

This command will:
1. Start Docker containers (PostgreSQL and Flask app)
2. Wait for PostgreSQL to be ready (up to 30 seconds)
3. Apply database migrations from `scripts/migrations.sql`
4. Wait for the Flask application to start
5. Verify application health by checking the health endpoint
6. Return JSON status report

**Example Output:**
```json
{
	"status": "Application deployed successfully"
}
```

### Check Application Health

After deployment, verify everything is working:

```bash
# Health check endpoint
curl http://localhost:8080/health

# Response
{"status":"ok"}
```

### Access the API

```bash
# Get data from the database
curl http://localhost:8080/data

# Response example
{
	"table": "users",
	"count": 1,
	"data": [
		{
			"id": 1,
			"name": "Test User"
		}
	]
}
```

### View Logs

```bash
# View logs from all containers
docker compose logs -f

# View logs from specific service
docker compose logs -f app
docker compose logs -f postgres
```

### Stop Application

```bash
docker compose down
```

Stops and removes all containers (data in named volumes is preserved).

### Stop with Data Cleanup

```bash
docker compose down -v
```

Removes containers and volumes (this will delete the database).

## Rollback

```bash
python deployctl.py rollback
```

Returns to the previous deployment state. Note: current implementation restarts containers with `up -d` command.

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_VERSION` | 18.1 | PostgreSQL image version |
| `DB_NAME` | app1_db | Database name |
| `DB_USER` | app1_user | Database user |
| `POSTGRES_PASS` | app1_pass | Database password |
| `DB_HOST` | localhost | Database host (use `postgres` in container) |
| `DB_PORT` | 5432 | Database port |
| `APP_TAG` | 28 | Docker image tag for Flask app |

## Docker Compose Services

### PostgreSQL Service

```yaml
postgres:
	image: postgres:${POSTGRES_VERSION}
	# Initialized with environment variables
	# Health check enabled
	# Data persisted (configure volumes)
```

**Port:** `127.0.0.1:5432` (accessible only from localhost)

### Flask App Service

```yaml
app:
	image: arklan/faoapp_flask:${APP_TAG}
	# Depends on PostgreSQL health check
	# Mounts local main.py for development
	# Listens on port 8080
```

**Ports:**
- `8080` → Flask app (public)
- `8000` → Additional service port

## Common Commands

```bash
# Deployment cycle
python deployctl.py up         # Deploy/start app
python deployctl.py rollback   # Rollback current deployment

# Container management
docker compose up              # Start containers
docker compose down            # Stop containers
docker compose restart         # Restart containers
docker compose ps              # List running containers

# Database access
docker exec -it postgres psql -U app1_user -d app1_db

# View application
curl http://localhost:8080/health
curl http://localhost:8080/data
```

## Troubleshooting

### Application won't start

```bash
# Check container logs
docker compose logs app

# Verify database is ready
docker compose logs postgres

# Inspect network
docker network inspect deploy-app1_default
```

### Database connection failed

```bash
# Check if PostgreSQL is running
docker compose ps

# Test connection manually
docker exec -it postgres psql -U app1_user -d app1_db -c "SELECT version();"
```

### Port already in use

```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Or change port in docker-compose.yaml
```

### Check Python dependencies

```bash
# List installed packages
pip list

# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

## Development

### Hot Reload

The Flask app source code (`main.py`) is mounted as a volume in the container. Changes are automatically reflected:

```bash
# Edit main.py
nano main.py

# Restart app container
docker compose restart app
```

### Database Migrations

To apply new migrations, add SQL to `scripts/migrations.sql` and redeploy:

```bash
# Add new SQL to scripts/migrations.sql
echo "CREATE TABLE products (id SERIAL, name VARCHAR(100));" >> scripts/migrations.sql

# Deploy (migrations run automatically)
python deployctl.py up
```

## Production Deployment

### Security Checklist

- [ ] Change all default passwords in `.env`
- [ ] Use Docker secrets or environment management service
- [ ] Set `DB_HOST=postgres` in `.env` (not localhost)
- [ ] Remove unnecessary ports from `docker-compose.yaml`
- [ ] Use production-grade Flask WSGI server (Gunicorn)
- [ ] Configure proper logging and monitoring
- [ ] Set resource limits in Docker Compose
- [ ] Use health checks for automatic restarts

### Example Production docker-compose.yaml

```yaml
services:
	postgres:
		image: postgres:${POSTGRES_VERSION}
		restart: unless-stopped
		deploy:
			resources:
				limits:
					cpus: '1'
					memory: 512M
		ports:
			- "5432:5432"  # Only internal network

	app:
		image: arklan/faoapp_flask:${APP_TAG}
		restart: unless-stopped
		deploy:
			resources:
				limits:
					cpus: '0.5'
					memory: 256M
		environment:
			FLASK_ENV: production
```

## Monitoring

### Health Check Status

```bash
# Check application health
python deployctl.py up

# Manual health check
curl -v http://localhost:8080/health
```

### Resource Usage

```bash
# Monitor container stats
docker stats

# View container resource limits
docker inspect app1 | grep -A 10 "HostConfig"
```

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## Troubleshooting Guide

### Issue: `psycopg2.OperationalError: could not connect to server`

**Solution:**
```bash
# Ensure PostgreSQL container is running
docker compose ps

# Check PostgreSQL logs
docker compose logs postgres

# Wait longer for database startup
# Increase retries in deployctl.py if needed
```

### Issue: `curl: (7) Failed to connect to localhost port 8080`

**Solution:**
```bash
# Verify containers are running
docker compose ps

# Check Flask app logs
docker compose logs app

# Verify port binding
docker port app1
```

### Issue: `ModuleNotFoundError: No module named 'psycopg2'`

**Solution:**
```bash
pip install psycopg2-binary python-dotenv Flask
```

## License

This project is part of the deployment infrastructure. See LICENSE file for details.

## Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting-guide) section
- Review Docker Compose documentation: https://docs.docker.com/compose/
- Review Flask documentation: https://flask.palletsprojects.com/
- Visit PostgreSQL docs: https://www.postgresql.org/docs/