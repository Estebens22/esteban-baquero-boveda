# 09 · Lleva tu proyecto a producción
### Contenedor, dominio, TLS y monitoreo — de "me funciona en mi máquina" a un sitio en vivo

**Categoría:** Infra · **Estado:** En producción · **Nivel:** principiante–intermedio

Este es el patrón real con el que vive [estebanbaquero.com](https://estebanbaquero.com): un contenedor nginx detrás de un reverse-proxy con TLS automático. Sin plataformas caras ni magia. Honesto: incluye los errores típicos que te vas a encontrar (403 por permisos, disco lleno por logs, cert que no emite).

## Qué vas a lograr
`Dockerfile → contenedor → reverse-proxy con TLS → dominio (DNS) → logs limitados → healthcheck`. Al final tienes tu app en vivo con HTTPS y dominio propio.

## Requisitos
- Un servidor (VPS) con **Docker**.
- Un **dominio** con acceso a su DNS.
- Un reverse-proxy con TLS automático (**Caddy** es el más simple) y acceso **SSH**.

## Paso a paso

**1. Contenerizá tu app.** Usa `kit/Dockerfile.example` como base (ajustá a tu stack). La clave anti-403:
```
RUN chmod -R a+rX /usr/share/nginx/html
```
nginx corre como usuario no-root; si los archivos vienen con permisos `600`, da **403**. El `a+rX` lo evita.

**2. Build + run con 1 comando.** Usa `kit/deploy.sh`:
```
./deploy.sh mi-app 8080
```
Hace build, corre el contenedor con **restart automático** y **logs limitados**, y te hace el healthcheck local.

**3. Límite de logs (no te saltes esto).** Un contenedor que loguea sin límite **llena el disco** y tumba todo. Por eso el `deploy.sh` corre con:
```
--log-opt max-size=10m --log-opt max-file=3
```

**4. DNS.** Apuntá un registro **A** de `tu-dominio.com` (y `www`) a la IP del servidor. Si usás Cloudflare, dejalo **DNS-only** (nube gris) para que el reverse-proxy pueda emitir el certificado por el challenge HTTP.

**5. TLS automático + reverse-proxy.** Agrega el bloque de `kit/Caddyfile.snippet` a tu Caddyfile y recargá Caddy. El certificado Let's Encrypt se emite solo al primer hit.

**6. Verificá en vivo** (no contra el pipeline verde, contra el dominio real):
```
curl -s -o /dev/null -w "%{http_code}\n" https://tu-dominio.com/
```

## Errores clásicos (y cómo salir)
| Síntoma | Causa típica | Solución |
|---|---|---|
| **403** en todo | permisos `600` de los archivos | `chmod -R a+rX` (ya en el Dockerfile) |
| El cert no emite | DNS mal / puerto 80 cerrado | A correcto + DNS-only + 80/443 abiertos |
| Disco al **100%** | logs del contenedor sin límite | `--log-opt max-size` + truncar el log |
| Contenedor en loop | la app crashea al arrancar | `docker logs <nombre>` |
| Redeploy tumba prod | sin rollback | guardá la imagen anterior / `git revert` + redeploy |

## Checklist
Ver `kit/checklist.md` — recorre todo antes de anunciar "está en vivo".

## Descargas
- **Kit:** `kit/` (deploy.sh, Dockerfile.example, Caddyfile.snippet, checklist, .env.example).
- También como **ZIP** en la [sección de releases](https://github.com/Estebens22/esteban-baquero-boveda) o el botón de la landing.

---
Hecho por **Esteban Baquero** · [estebanbaquero.com](https://estebanbaquero.com) · De una idea a un sistema que funciona.
Si te sirvió, **seguime y dale ⭐** → [github.com/Estebens22](https://github.com/Estebens22)
