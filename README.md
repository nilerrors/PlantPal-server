# Management

## Start Serve

```Powershell
uvicorn api:app --reload --host 0.0.0.0 --ssl-keyfile .\key.pem --ssl-certfile .\cert.pem
```

## Setup

### Environment

```Powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### .env

```sh
AUTHJWT_SECRET_KEY=""

MAIL_USERNAME=""
MAIL_PASSWORD=""
MAIL_FROM=""
MAIL_PORT=587
MAIL_SERVER=smtp.office365.com
MAIL_FROM_NAME="PlantPal"

DATABASE_URL="postgresql://postgres:postgres@localhost:5432/plantpal"
```

in `./src/prisma/.env`

```sh
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/plantpal"
```

### Database

```Powershell
# Generate
prisma generate --schema=.\src\prisma\schema.prisma

# Migrate dev
prisma migrate dev --name=init --schema=.\src\prisma\schema.prisma

# Migrate prod
prisma migrate prod --name=init --schema=.\src\prisma\schema.prisma
```
