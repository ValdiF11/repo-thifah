import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    print(f"\n========================================================")
    print(f"🚀 AI 3D Event Layout Studio Berhasil Dijalankan!")
    print(f"🔗 Buka di browser: http://localhost:{port}")
    print(f"📚 Dokumentasi API: http://localhost:{port}/docs")
    print(f"========================================================\n")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)

