# Helpdesk API

Backend completo para sistema de gestión de tickets (Helpdesk) construido con FastAPI y PostgreSQL.

## Stack Tecnológico

- **Python** 3.9+
- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional
- **SQLAlchemy** - ORM para mapeo de modelos
- **Pydantic** - Validación de datos
- **JWT** - Autenticación basada en tokens
- **bcrypt** - Hash de contraseñas

## Estructura del Proyecto

```
app/
├── __init__.py
├── main.py              # Punto de entrada de la aplicación
├── database.py          # Configuración de conexión a PostgreSQL
├── models/              # Modelos SQLAlchemy
│   └── __init__.py      # User, Category, Ticket, TicketComment, TicketHistory
├── schemas/             # Schemas Pydantic
│   └── __init__.py      # DTOs para validación
├── routes/              # Endpoints de la API
│   ├── __init__.py
│   ├── auth.py          # Login JWT
│   ├── users.py         # Gestión de usuarios
│   ├── tickets.py       # Gestión de tickets
│   ├── categories.py    # Gestión de categorías
│   └── reports.py       # Reportes y estadísticas
├── services/            # Lógica de negocio
│   ├── __init__.py
│   ├── user_service.py
│   ├── category_service.py
│   ├── ticket_service.py
│   └── report_service.py
└── core/                # Utilidades core
    ├── __init__.py
    ├── security.py      # JWT y bcrypt
    └── auth.py          # Middleware de autenticación
```

## Instalación

1. **Clonar el repositorio y entrar al directorio:**

```bash
cd /Users/pedrozapata/Documents/Apps/soporte360
```

2. **Crear entorno virtual e instalar dependencias:**

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**

```bash
cp .env.example .env
# Editar .env con tus credenciales de PostgreSQL
```

4. **Ejecutar la aplicación:**

```bash
uvicorn app.main:app --reload
```

La API estará disponible en: http://localhost:8000

Documentación interactiva (Swagger UI): http://localhost:8000/docs

## Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql://user:pass@localhost:5432/helpdesk` |
| `SECRET_KEY` | Clave secreta para JWT | `your-secret-key` |

## Roles y Permisos

- **ADMIN**: Crear usuarios, categorías, ver todo
- **SUPERVISOR**: Ver todos los tickets, ver reportes
- **TECNICO**: Ver tickets asignados, actualizar estado, comentar
- **USUARIO**: Crear tickets, ver sus tickets, comentar

## Endpoints Principales

### Auth
- `POST /auth/login` - Login con email y password

### Usuarios (ADMIN)
- `POST /users` - Crear usuario
- `GET /users` - Listar usuarios
- `POST /users/bulk` - Crear usuarios desde CSV
- `PUT /users/{id}/activate` - Activar usuario
- `PUT /users/{id}/deactivate` - Desactivar usuario

### Tickets
- `POST /tickets` - Crear ticket (auto-asigna al técnico con menor carga)
- `GET /tickets` - Listar tickets (filtrado por rol)
- `GET /tickets/{id}` - Ver detalle de ticket
- `PUT /tickets/{id}/status` - Cambiar estado
- `PUT /tickets/{id}/assign` - Asignar técnico
- `POST /tickets/{id}/comments` - Agregar comentario
- `GET /tickets/{id}/comments` - Ver comentarios
- `GET /tickets/{id}/history` - Ver historial

### Categorías (ADMIN)
- `POST /categories` - Crear categoría
- `GET /categories` - Listar categorías

### Reportes (SUPERVISOR+)
- `GET /reports/general` - Estadísticas generales
- `GET /reports/by-category` - Tickets por categoría
- `GET /reports/by-technician` - Tickets por técnico

## Características Implementadas

- ✅ Mapeo exacto de tablas PostgreSQL existentes
- ✅ Autenticación JWT con bcrypt
- ✅ Control de acceso basado en roles
- ✅ Asignación automática de tickets al técnico con menor carga
- ✅ Registro automático de historial (creación, cambios, asignaciones, comentarios)
- ✅ Reportes eficientes con SQL GROUP BY
- ✅ Validación de datos con Pydantic
- ✅ Manejo de errores HTTP apropiado

## Notas Importantes

- **NO** se crean ni modifican tablas en la base de datos
- El `ticket_code` se genera mediante trigger de PostgreSQL
- El campo `closed_at` se llena automáticamente al pasar a estado CLOSED
- Los enums de PostgreSQL se mapean correctamente con SQLAlchemy
