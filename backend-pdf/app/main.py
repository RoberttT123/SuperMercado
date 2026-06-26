from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .pdf_generator import crear_pdf_venta

app = FastAPI()

# Permitir CORS para que tu frontend en Vue pueda conectar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generar-pdf")
async def generar_pdf(request: Request):
    try:
        data = await request.json()
        
        # Recibimos los datos del JSON (que enviará Vue.js)
        items = data.get("items")
        total = data.get("total")
        numero_venta = data.get("numero_venta")
        cliente = data.get("cliente")
        
        # Generar los bytes
        pdf_bytes = crear_pdf_venta(items, total, numero_venta, cliente)
        
        # Responder con el archivo binario
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=venta_{numero_venta}.pdf"}
        )
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health():
    return {"status": "ok"}