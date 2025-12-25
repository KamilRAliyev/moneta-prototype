# Environment Variables

This document lists all environment variables used in the Moneta project, their purpose, and sample values.

## Database Configuration

| Variable | Purpose | Default | Sample Value | Required |
|----------|---------|---------|--------------|----------|
| `DB_HOST` | PostgreSQL server hostname | `localhost` | `postgres` (in Docker) or `localhost` | No |
| `DB_PORT` | PostgreSQL server port | `5432` | `5432` | No |
| `DB_USER` | PostgreSQL username | `postgres` | `postgres` | No |
| `DB_PASSWORD` | PostgreSQL password | `` (empty) | `mysecurepassword123` | No* |
| `DB_NAME` | Database name | `moneta` | `moneta` | No |
| `DB_POOL_SIZE` | Connection pool size | `5` | `10` | No |
| `DB_MAX_OVERFLOW` | Max overflow connections | `10` | `20` | No |
| `DB_POOL_PRE_PING` | Enable connection health checks | `true` | `true` or `false` | No |
| `DB_ECHO` | Echo SQL queries (for debugging) | `false` | `true` or `false` | No |

\* Required if `DB_PASSWORD` is set in production

## PostgreSQL Container (Docker Compose)

| Variable | Purpose | Default | Sample Value | Required |
|----------|---------|---------|--------------|----------|
| `POSTGRES_USER` | PostgreSQL superuser | - | `postgres` | Yes |
| `POSTGRES_PASSWORD` | PostgreSQL superuser password | - | `mysecurepassword123` | Yes |
| `POSTGRES_DB` | Initial database name | - | `moneta` | Yes |

## pgAdmin Configuration

| Variable | Purpose | Default | Sample Value | Required |
|----------|---------|---------|--------------|----------|
| `PGADMIN_CONFIG_MASTER_PASSWORD_REQUIRED` | Require master password | - | `False` | No |
| `PGADMIN_DEFAULT_EMAIL` | pgAdmin login email | - | `admin@moneta.local` | No |
| `PGADMIN_DEFAULT_PASSWORD` | pgAdmin login password | - | `admin123` | No |

## Application Configuration

| Variable | Purpose | Default | Sample Value | Required |
|----------|---------|---------|--------------|----------|
| `PORT` | Application server port | `8000` | `8000` | No |
| `ENV_FILE` | Path to environment file | - | `/app/env/dev.env` | No |
| `APP_VERSION` | Application version | `0.1.0` | `0.1.0` | No |
| `ENVIRONMENT` | Environment name (dev, staging, prod) | `development` | `development` | No |
| `DATA_DIR` | Path to persistent data directory | `/data` | `/data` | No |

## Grafana Configuration (if used)

| Variable | Purpose | Default | Sample Value | Required |
|----------|---------|---------|--------------|----------|
| `GF_SECURITY_ADMIN_USER` | Grafana admin username | - | `admin` | No |
| `GF_SECURITY_ADMIN_PASSWORD` | Grafana admin password | - | `admin123` | No |

## Notes

- **Database Variables**: The `DB_*` variables are used by the application to connect to PostgreSQL
- **PostgreSQL Variables**: The `POSTGRES_*` variables are used by the PostgreSQL Docker container
- **Connection Pooling**: `DB_POOL_SIZE` and `DB_MAX_OVERFLOW` control how many database connections can be open simultaneously
- **Pre-ping**: `DB_POOL_PRE_PING=true` ensures connections are healthy before use (recommended for production)
- **SQL Echo**: `DB_ECHO=true` logs all SQL queries (useful for debugging, disable in production)

## Environment File Structure

Environment variables are typically loaded from:
- Development: `env/dev.env`
- Production: Set via deployment platform (Kubernetes secrets, Docker secrets, etc.)

The application loads variables from the file specified by `ENV_FILE` environment variable.

## Security Notes

- Never commit `.env` files with real passwords to version control
- Use strong passwords in production
- Consider using secrets management (Kubernetes secrets, AWS Secrets Manager, etc.) in production
- The `dev.env.template` file shows required variables without actual values
