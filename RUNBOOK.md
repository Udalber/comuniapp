# Runbook — Encender ComuniApp para pruebas



Documento operativo para **agentes y desarrolladores** que necesitan levantar el proyecto en local, verificar que funciona y hacer pruebas manuales.

**Despliegue en producción (Render):** ver [DEPLOY.md](DEPLOY.md).



**Ruta del proyecto (absoluta):** `c:\Users\anudr\Documents\IBERO\comuniapp`



**Convenciones de código:** ver `README.md`.



> **Nota para agentes (puerto fijo):** Al ejecutar pruebas desde Cursor/terminal, usa **siempre el puerto `8765`** (`python manage.py runserver 8765`). Los comandos `Invoke-WebRequest` y enlaces de este runbook apuntan a `http://127.0.0.1:8765/` para que coincidan con el servidor que dejas en segundo plano. Si levantas el servidor en otro puerto, sustituye `8765` en cada URL de este documento.



---



## 1. Requisitos previos



| Requisito | Cómo comprobarlo |

|-----------|------------------|

| Python 3.11 o superior | `python --version` |

| Git (opcional, para clonar/actualizar) | `git --version` |

| Puerto **8765** libre (puerto de pruebas de agentes) | No debe haber otro `runserver` en ese puerto |



No hace falta PostgreSQL para pruebas locales: por defecto se usa **SQLite** (`db.sqlite3` en la raíz del proyecto).



---



## 2. Primera vez (setup completo)



Ejecutar **desde la raíz del proyecto** (`comuniapp/`). En PowerShell (Windows):



```powershell

cd c:\Users\anudr\Documents\IBERO\comuniapp



python -m venv .venv

.\.venv\Scripts\Activate.ps1



pip install -r requirements.txt



# Opcional: variables de entorno (si no existe .env, Django usa valores por defecto en settings)

if (-not (Test-Path .env)) { Copy-Item .env.example .env }



python manage.py migrate

python manage.py check

```



En bash (Linux/macOS):



```bash

cd /ruta/a/comuniapp

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

cp -n .env.example .env 2>/dev/null || true

python manage.py migrate

python manage.py check

```



**Criterio de éxito del setup:** `python manage.py check` termina con `System check identified no issues`.



---



## 3. Encender el servidor (cada sesión de pruebas)



### 3.1 Puerto recomendado para agentes y este runbook



```powershell

cd c:\Users\anudr\Documents\IBERO\comuniapp

.\.venv\Scripts\Activate.ps1

python manage.py runserver 8765

```



Salida esperada:



```text

Starting development server at http://127.0.0.1:8765/

Quit the server with CTRL-BREAK.

```



**URL base para pruebas (usar en navegador y en comandos de este runbook):** http://127.0.0.1:8765/



**Detener el servidor:** `Ctrl+C` (o `Ctrl+Break` en Windows) en la terminal donde corre `runserver`. Si el agente lo lanzó en segundo plano, cerrar ese proceso antes de iniciar otro `runserver` en el mismo puerto.



### 3.2 Puerto alternativo (desarrollo humano)



Si prefieres el puerto por defecto de Django:



```powershell

python manage.py runserver

```



→ http://127.0.0.1:8000/ — en ese caso **sustituye `8765` por `8000`** en las secciones 4 y 5 de este runbook.



---



## 4. Verificación rápida (Definition of Done operativo)



### 4.1 Comprobaciones en terminal (agente)



Con el venv activado y **sin necesidad** de que el servidor esté arriba para migrate/check:



```powershell

python manage.py check

python manage.py showmigrations accounts

```



`showmigrations accounts` debe mostrar `[X] 0001_initial` (migración del usuario custom aplicada).



Con el servidor **encendido en el puerto 8765**, comprobar HTTP (PowerShell):



```powershell

(Invoke-WebRequest -Uri "http://127.0.0.1:8765/" -UseBasicParsing).StatusCode

```



Debe devolver `200`.



Comprobar que cargan los estáticos del diseño:



```powershell

$r = Invoke-WebRequest -Uri "http://127.0.0.1:8765/" -UseBasicParsing

$r.Content -match "design.css"

$r.Content -match "ComuniApp"

```



Ambas expresiones deben ser `True`.



Comprobar pantallas de autenticación (sesión A):



```powershell

$login = Invoke-WebRequest -Uri "http://127.0.0.1:8765/accounts/login/" -UseBasicParsing

$login.StatusCode -eq 200

$login.Content -match "auth.css"

$login.Content -match 'data-auth-form="login"'



$reg = Invoke-WebRequest -Uri "http://127.0.0.1:8765/accounts/register/" -UseBasicParsing

$reg.StatusCode -eq 200

$reg.Content -match 'data-auth-form="register"'

```



### 4.2 Comprobaciones visuales (humano o agente con navegador)



Usar **http://127.0.0.1:8765/** (o el puerto que hayas elegido de forma consistente).



| Prueba | Qué validar |

|--------|-------------|

| Landing `/` | Hero, buscador, botón «Explorar catálogo», grid de categorías placeholder |

| Estilos | Fondo crema (`--bg-page`), verde primario en logo/botones, fuente **Inter** |

| Navbar (anónimo) | «Iniciar sesión» y «Registrarse» enlazan a login/registro |

| Registro `/accounts/register/` | Panel verde izquierda (desktop); validación en vivo; medidor de contraseña; toggle mostrar/ocultar |

| Login `/accounts/login/` | Botón deshabilitado con campos vacíos; error genérico con credenciales malas |

| Navbar (autenticado) | Nombre de usuario, dropdown, «Cerrar sesión» |

| Toasts | Tras registro/login, mensaje visible arriba a la derecha |

| Móvil (&lt;768px) | Auth en una columna; hamburguesa en navbar |

| Escritorio (&gt;1024px) | Auth en dos columnas; categorías en 3 columnas en home |



**Responsive en el navegador:** DevTools → modo dispositivo → probar ~375px, ~768px, ~1280px.



### 4.3 Rutas que existen hoy vs. stubs



| URL | Comportamiento actual |

|-----|------------------------|

| `/` | Landing funcional |

| `/admin/` | Django admin (requiere `createsuperuser`) |

| `/accounts/register/` | Registro (RF-001) |

| `/accounts/login/` | Login (RF-002) |

| `/accounts/logout/` | Solo POST (desde navbar autenticado) |

| `/accounts/password-reset/` | Placeholder «próximamente» |

| `/accounts/` (raíz) | Sin vista → 404 (normal; usar rutas nombradas arriba) |

| `/catalog/`, `/cart/` | Stubs sin vistas → 404 esperado |



---



## 5. Pruebas manuales — Autenticación (sesión A)



Servidor en **http://127.0.0.1:8765/**.



### 5.1 Registro



1. Abrir http://127.0.0.1:8765/accounts/register/

2. Completar nombre, correo nuevo y contraseña (probar medidor débil/media/fuerte).

3. Pulsar **Crear cuenta**.

4. Verificar: redirect a `/`, toast de bienvenida, navbar con tu nombre.



### 5.2 Login y recordarme



1. Cerrar sesión desde el menú de usuario.

2. Abrir http://127.0.0.1:8765/accounts/login/

3. Comprobar que el botón está deshabilitado hasta llenar correo y contraseña.

4. Iniciar sesión con el usuario creado (probar con y sin «Recordarme»).

5. Probar credenciales incorrectas → un solo mensaje genérico, sin indicar qué campo falló.



### 5.3 Regresión sesión 0



1. Abrir http://127.0.0.1:8765/ — landing, navbar sticky y footer sin roturas visuales.

2. En móvil, menú hamburguesa sigue funcionando.



---



## 6. Admin (opcional, para pruebas de `accounts.User`)



Solo la primera vez o cuando haga falta un usuario de prueba:



```powershell

python manage.py createsuperuser

```



Luego abrir http://127.0.0.1:8765/admin/ e iniciar sesión (admin usa **username**, no el flujo de correo de la app).



---



## 7. Problemas frecuentes y solución



| Síntoma | Causa probable | Acción |

|---------|----------------|--------|

| `Couldn't import Django` | venv no activado o dependencias sin instalar | Activar `.venv` y `pip install -r requirements.txt` |

| `Dependency on app with no migrations: accounts` | Falta migración de accounts | `python manage.py makemigrations accounts` luego `migrate` |

| `Port already in use` | Otro proceso en **8765** (o 8000) | Cerrar el `runserver` anterior o usar otro puerto y actualizar URLs del runbook |

| Enlaces del runbook no cargan | Servidor en 8000 pero runbook dice 8765 | Usar `runserver 8765` o cambiar puerto en los comandos |

| `No module named 'dotenv'` / `dj_database_url` | requirements incompletos | `pip install -r requirements.txt` |

| Página sin estilos | URL incorrecta o caché | Confirmar `DEBUG=True`; recargar forzado; revisar `/static/css/design.css` |

| `ValueError: multiple authentication backends` al registrar | Falta `backend=` en `login()` | Debe estar corregido en `accounts/views.py` (sesión A) |

| `InconsistentMigrationHistory` tras cambiar `AUTH_USER_MODEL` | BD creada antes del user custom | **Solo en dev:** borrar `db.sqlite3` y volver a `python manage.py migrate` |

| Error al activar venv en PowerShell | Política de ejecución | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` o usar `.\.venv\Scripts\python.exe` directamente |



**Regla crítica para agentes:** no cambiar `AUTH_USER_MODEL` ni borrar `accounts/migrations/0001_initial.py` en un entorno que ya tiene datos reales.



---



## 8. Flujo recomendado para un agente que implementa una feature



1. `cd` a `comuniapp` y activar venv.

2. `python manage.py check`

3. Si tocó modelos: `makemigrations` → `migrate`

4. `python manage.py runserver 8765` en segundo plano o terminal dedicada (**puerto 8765** para alinear con este runbook).

5. Probar URLs nuevas con `http://127.0.0.1:8765/...` + regresión en `/` (navbar/footer/estilos).

6. Al terminar, **detener** el `runserver` (`Ctrl+C` o cerrar el proceso en segundo plano).

7. No commitear `.env`, `db.sqlite3` ni `.venv/` (ya están en `.gitignore`).



---



## 9. Variables de entorno (referencia)



Archivo plantilla: `.env.example`. Copia a `.env` si necesitas sobrescribir valores.



| Variable | Uso en local |

|----------|----------------|

| `SECRET_KEY` | Opcional en dev (hay fallback en settings) |

| `DEBUG` | `True` para desarrollo |

| `ALLOWED_HOSTS` | `localhost,127.0.0.1` |

| `DATABASE_URL` | Omitir → SQLite en `db.sqlite3` |



---



## 10. Checklist copiable (antes de decir «listo para pruebas»)



```

[ ] cd comuniapp + venv activado

[ ] pip install -r requirements.txt (si hubo cambios en requirements)

[ ] python manage.py migrate

[ ] python manage.py check → 0 issues

[ ] python manage.py runserver 8765 → sin traceback

[ ] GET http://127.0.0.1:8765/ → HTTP 200

[ ] HTML incluye design.css y texto ComuniApp

[ ] GET /accounts/login/ y /accounts/register/ → HTTP 200 + auth.css

[ ] Registro o login manual OK (si sesión auth tocada)

[ ] Navbar y footer visibles; responsive probado en al menos un ancho móvil

[ ] runserver detenido al cerrar la tarea (si se usó segundo plano)

```



---



## 11. Pruebas automatizadas (sesión F)



Con el venv activado, desde la raíz del proyecto:



```powershell

python manage.py test

```



**Resultado esperado:** `Ran 34 tests` — todos OK. Cubre unitarias (accounts, catalog, cart, orders) e integración del flujo MAZE (registro → compra → historial).



---



## 12. Referencias



| Documento | Contenido |

|-----------|-----------|

| [IMPLEMENTATION_SPEC.md](IMPLEMENTATION_SPEC.md) | Spec maestra (fundación + índice sesiones) |

| [DEPLOY.md](DEPLOY.md) | Despliegue en Render y URL pública |

| [IMPLEMENTATION_SPEC_SESSION_F.md](IMPLEMENTATION_SPEC_SESSION_F.md) | Pruebas + despliegue Render |

| [IMPLEMENTATION_SPEC_SESSION_A.md](IMPLEMENTATION_SPEC_SESSION_A.md) | Detalle técnico sesión A — autenticación |

| [README.md](README.md) | Arquitectura y convenciones |

| Prototipo UI | https://www.figma.com/design/sUIJIYy4Wf3Y7oI0oWeH41 |

| Settings | `config/settings.py` |

| Plantilla base | `core/templates/core/base.html` |

| Tokens CSS | `core/static/css/design.css` |


