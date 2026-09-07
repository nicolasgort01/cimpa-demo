"""Registra en HubSpot cada acceso al demo.

Por qué existe: `visit_log.json` se escribe en el disco del contenedor de
Streamlit Cloud, que es efímero — se borra cuando la app duerme (12h sin uso) o
se redespliega. Cada acceso quedaba registrado y se perdía.

Eso importa más de lo que parece. En Smartlead el tracking de aperturas y clics
está apagado a propósito para cuidar la entregabilidad, así que la única señal
de interés era que alguien respondiera un correo. Que un prospecto entre al
demo hecho a su medida es una señal mucho más fuerte — y se estaba tirando.

El acceso se anota contra el NEGOCIO, no contra un contacto, porque el demo usa
un usuario compartido por empresa: se sabe que entró alguien de CIMPA, no quién.

Regla de oro: esto NUNCA puede romper el demo. Si HubSpot no responde, si falta
el token o si cambia la API, el prospecto no se entera de nada. Por eso todo va
dentro de try/except con timeout corto.
"""
import json
import urllib.request
from datetime import datetime, timezone

BASE = "https://api.hubapi.com"
TIMEOUT = 3   # el prospecto siente cualquier retardo al entrar: corto a propósito

# Qué usuario del demo corresponde a qué negocio en HubSpot.
NEGOCIOS = {
    "cimpa_demo": ("223623619571", "CIMPA"),
}


def _token():
    """El token sale de los secretos de Streamlit o del entorno."""
    try:
        import streamlit as st
        t = st.secrets.get("HUBSPOT_TOKEN", "")
        if t:
            return str(t).strip()
    except Exception:
        pass
    import os
    return os.environ.get("HUBSPOT_TOKEN", "").strip()


def registrar_visita(username, name, ip, ciudad, region, pais):
    """Deja una nota en el negocio. Devuelve True si quedó registrada.

    Silencioso a propósito: el valor de esta función es que el equipo comercial
    se entere, no que el visitante vea un error si algo falla.
    """
    try:
        destino = NEGOCIOS.get(username)
        token = _token()
        if not destino or not token:
            return False
        deal_id, empresa = destino

        ahora = datetime.now(timezone.utc)
        lugar = " · ".join(x for x in (ciudad, region, pais) if x and x != "—")
        cuerpo = (
            f"<b>Acceso al demo de {empresa}</b><br><br>"
            f"Alguien entró al demo con el usuario <code>{username}</code>"
            f"{f' ({name})' if name else ''}.<br>"
            f"Fecha: {ahora.strftime('%Y-%m-%d %H:%M')} UTC<br>"
            f"Desde: {lugar or 'ubicación desconocida'}"
            f"{f' · IP {ip}' if ip else ''}<br><br>"
            "<i>Señal de interés fuerte: está mirando la propuesta. "
            "Buen momento para hacer seguimiento.</i>"
        )

        req = urllib.request.Request(
            f"{BASE}/crm/v3/objects/notes",
            method="POST",
            data=json.dumps({
                "properties": {
                    "hs_note_body": cuerpo,
                    "hs_timestamp": ahora.isoformat(),
                },
                "associations": [{
                    "to": {"id": deal_id},
                    "types": [{"associationCategory": "HUBSPOT_DEFINED",
                               "associationTypeId": 214}],
                }],
            }).encode(),
            headers={"Authorization": f"Bearer {token}",
                     "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT):
            return True
    except Exception:
        # A propósito: ningún fallo aquí puede llegarle al prospecto.
        return False
