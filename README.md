# Centro de Comunicaciones de Campaña

MVP web para organizar cuatro módulos prioritarios:

1. Inteligencia
2. Monitoreo de medios
3. Producción de contenidos
4. Prensa

## Tecnología
- Python 3.11+
- Streamlit
- SQLite
- Feedparser para RSS
- Pandas

La arquitectura está pensada para ser clara y ampliable. No depende de una plataforma cerrada.

## Instalación

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

La aplicación crea automáticamente `data/campana.db`.

## Próximas integraciones
- Google News/RSS y fuentes institucionales.
- APIs de redes sociales.
- Gmail/Outlook.
- Generación asistida de contenidos mediante API.
- Alertas por correo/Telegram/WhatsApp Business.
- Roles y autenticación.
- Dashboard histórico.
