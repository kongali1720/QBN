import json
import os
import uuid
import pytz
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

# --- CONFIGURATION & DATABASE ---
DB_FILE = "database_anc.json"

def save_to_db(data):
    transactions = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try: transactions = json.load(f)
            except: transactions = []
    transactions.append(data)
    with open(DB_FILE, "w") as f:
        json.dump(transactions, f, indent=4)

# --- APP INITIALIZATION ---
app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
    version="0.5.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
USER_DATA = {"admin": "Arjuna2026!"}

# --- SCHEMAS ---
class Address(BaseModel):
    country: str; city: str; firstLine: str; state: str; postCode: str

class AccountDetails(BaseModel):
    legalType: str; abartn: str; accountNumber: str; accountType: str; address: Address; email: str

class RecipientAccount(BaseModel):
    currency: str; type: str; profile: int; ownedByCustomer: bool; accountHolderName: str; details: AccountDetails

class QuoteRequest(BaseModel):
    sourceCurrency: str; targetCurrency: str; sourceAmount: Optional[float] = None; targetAmount: float; payOut: str; preferredPayIn: str; targetAccount: int; paymentMetadata: Optional[Dict] = None

class TransferRequest(BaseModel):
    targetAccount: int; quoteUuid: str; customerTransactionId: str; details: Dict

class CryptoConfirmation(BaseModel):
    network: str; asset_type: str; amount: float; transaction_hash: str; payout_master_wallet: str

class CardTransaction(BaseModel):
    card_id: str; status: str; balance: float; currency: str; payout_wallet: str; metadata: Dict

class FiatTransfer(BaseModel):
    sender_bank: str; account_name: str; amount: float; currency: str; swift_code: str; payout_wallet: str

class VmmlTransaction(BaseModel):
    card_number: str; amount: float; payout_master_wallet: str; metadata: Dict

class FundTransferRequest(BaseModel):
    type: str = "BALANCE"

class RemittanceReceiver(BaseModel):
    externalId: str; firstName: str; lastName: str; email: str; dob: str; phoneNumber: Optional[str]; companyName: str; address: Dict; accountNumber: str

class CreateRemittanceRequest(BaseModel):
    senderBankOfficerFullName: str; receiverDetails: RemittanceReceiver; correspondentBankId: str; bankId: str; remittanceType: str = "DEBIT"

# --- CUSTOM SWAGGER UI ---
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    app.openapi_schema = None
    wib = pytz.timezone('Asia/Jakarta')
    init_time = datetime.now(wib).strftime("%A, %B %d, %Y at %H:%M:%S WIB")

    app.description = f"""
<style>
    html, body, .swagger-ui {{ background-color: #0d1117 !important; color: #ffffff !important; }}
    .swagger-ui .info .title, .swagger-ui .info p, .swagger-ui .info li,
    .swagger-ui .opblock-tag, .swagger-ui .opblock .opblock-summary-path,
    .swagger-ui .opblock .opblock-summary-description, .swagger-ui .btn,
    .swagger-ui label, .swagger-ui .model-title, .swagger-ui .prop-name,
    .swagger-ui .opblock-description-wrapper p, .swagger-ui .tabli button {{
        color: #ffffff !important;
    }}
    .swagger-ui .opblock {{ background: #161b22 !important; border: 1px solid #30363d !important; }}
    .swagger-ui .scheme-container {{ background: #161b22 !important; border-bottom: 1px solid #30363d !important; box-shadow: none !important; }}
    .swagger-ui select, .swagger-ui input {{ background: #0d1117 !important; color: white !important; border: 1px solid #30363d !important; }}
    .swagger-ui .topbar {{ display: none; }}
</style>

<center>
<div style="margin-bottom: 30px; border-bottom: 2px solid #0d47a1; padding-bottom: 20px;">
    <img src="https://raw.githubusercontent.com/kongali1720/QBN/main/logo-coin03.png" width="150" title="QUANTUM BLOCKCHAIN NUSANTARA">
</div>

<div style="background: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #30363d; max-width: 950px; margin-bottom: 30px;">
    <p style="color: #58a6ff; font-size: 13px; font-weight: bold; letter-spacing: 2px; margin-bottom: 25px; text-transform: uppercase;">Supported Native Assets & Protocols</p>
    <div style="display: flex; justify-content: center; align-items: center; gap: 40px; flex-wrap: wrap;">
        <img src="https://raw.githubusercontent.com/kongali1720/ANC/main/logo.jpg" width="85">
        <img src="https://raw.githubusercontent.com/kongali1720/kongalicoin/main/kongalicoin.jpeg" width="85" style="border-radius:50%;">
        <img src="https://raw.githubusercontent.com/kongali1720/QBN/main/logo-coin03.png" width="85" style="border-radius:50%;">
        <img src="https://raw.githubusercontent.com/kongali1720/ATEKACOIN/main/black-logo-ateka.jpg" width="95" style="border-radius:50%;">
        <img src="https://cryptologos.cc/logos/ethereum-eth-logo.svg" width="50" style="filter: brightness(1.5);">
    </div>
</div>

<h2 style="color: #58a6ff; font-weight: bold;">Quantum Institutional Asset Settlement Protocol (OAS 3.1)</h2>
<div style="color: #ffffff;">🌐 Status: <span style="color: #3fb950; font-weight: bold;">🟢 [OPERATIONAL]</span> | 🕒 Heartbeat: <span id="live-clock" style="color: #d29922;">{init_time}</span></div>

<div style="background: rgba(210,153,34,0.1); padding: 12px; border-radius: 6px; border: 1px solid #d29922; margin-top: 20px; max-width: 950px; text-align: left;">
<marquee style="color: #d29922; font-weight: bold;">⚠️ NOTICE: ISO 20022 Standard Active. Workflow Compliant with Quantum Blockchain Network. ⚠️</marquee>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 25px; max-width: 950px; text-align: left;">
    <div style="background: #0d1117; padding: 20px; border-radius: 12px; border: 1px solid #30363d;">
        <h4 style="color: #3fb950; margin-top: 0;">🏦 FIAT SETTLEMENT</h4>
        <b>Beneficiary:</b> QUANTUM BLOCKCHAIN NUSANTARA<br>
        <b>A/C:</b> 1270588988905 (USD)<br>
        <b>Bank:</b> Mandiri | <b>Swift:</b> BMRIIDJA
        <div style="margin-top: 20px; display: flex; align-items: center; gap: 15px; border-top: 1px solid #30363d; padding-top: 15px; flex-wrap: wrap; filter: brightness(1.1);">
            <img src="https://upload.wikimedia.org/wikipedia/id/f/fa/Bank_Mandiri_logo.svg" height="30">
            <img src="https://upload.wikimedia.org/wikipedia/commons/f/f0/Bank_Negara_Indonesia_logo_%282004%29.svg" height="30">
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/aa/HSBC_logo_%282018%29.svg" height="30">
            <img src="https://upload.wikimedia.org/wikipedia/commons/7/7b/Deutsche_Bank_logo_without_wordmark.svg" height="30">
            <img src="https://upload.wikimedia.org/wikipedia/en/7/7e/Barclays_logo.svg" height="25">
            <img src="https://upload.wikimedia.org/wikipedia/en/thumb/a/ab/UBS_Logo.svg/512px-UBS_Logo.svg.png" height="30">
        </div>
    </div>
    <div style="background: #0d1117; padding: 20px; border-radius: 12px; border: 1px solid #30363d;">
        <h4 style="color: #58a6ff; margin-top: 0;">🔐 DIGITAL ASSET</h4>
        <b>Network:</b> ERC-20 / BEP-20<br>
        <b>Wallet:</b> <code style="color: #f85149;">0x5448c44c2088f43d651dbeAACee99aFf5fEC95c6</code>
        <div style="margin-top: 20px; display: flex; align-items: center; gap: 25px; border-top: 1px solid #30363d; padding-top: 15px; filter: brightness(1.2);">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/5c/Visa_Inc._logo_%282021%E2%80%93present%29.svg" height="35">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Mastercard-logo.svg/640px-Mastercard-logo.svg.png" height="35">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/American_Express_logo_%282018%29.svg/640px-American_Express_logo_%282018%29.svg.png" height="35">
        </div>
    </div>
</div>

<div style="margin-top: 30px; text-align: left; max-width: 950px; border-top: 1px solid #30363d; padding-top: 20px; color: #ffffff;">
    <h4 style="color: #58a6ff; margin-bottom: 10px;">🛡️ COMPLIANCE & SECURITY</h4>
    <p style="margin: 5px 0;"><b>Authorized Signatory:</b> QUANTUM ADMINISTRATION</p>
    <p style="margin: 5px 0;">
        <b>Web:</b> <a href="https://quantumblockchainnusantara.com" target="_blank" style="color: #58a6ff; text-decoration: none; font-weight: bold;">quantumblockchainnusantara.com</a> |
        <b>Email:</b> <a href="mailto:info@quantumblockchainnusantara.com" style="color: #58a6ff; text-decoration: none; font-weight: bold;">info@quantumblockchainnusantara.com</a>
    </p>
    <div style="margin-top: 20px;">
        <a href="/docs/guide" target="_blank" style="background: #3fb950; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 13px; display: inline-block;">📘 VIEW IMPLEMENTATION METHODOLOGY (DOCS)</a>
    </div>
    <p style="margin-top: 15px; color: #8b949e; font-size: 12px;">🛡️ Verified by Quantum Security Protocol. Grade 0.5.1</p>
</div>
</center>

<script>
    function startClock() {{
        setInterval(function() {{
            var now = new Date();
            var options = {{ weekday: 'long', year: 'numeric', month: 'long', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false, timeZone: 'Asia/Jakarta' }};
            document.getElementById('live-clock').innerHTML = new Intl.DateTimeFormat('en-GB', options).format(now) + ' WIB';
        }}, 1000);
    }}
    setTimeout(startClock, 1000);
</script>
"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Quantum Institutional Gateway",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"
    )

@app.on_event("startup")
def setup_openapi():
    from fastapi.openapi.utils import get_openapi
    schema = get_openapi(title="Quantum Institutional Gateway", version="0.5.1", description=app.description, routes=app.routes)
    schema["servers"] = [{"url": "/"}]
    app.openapi_schema = schema

# --- DOCUMENTATION ENDPOINT (DETAILED) ---
@app.get("/docs/guide", include_in_schema=False, response_class=HTMLResponse)
async def get_onboarding_guide():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Implementation Methodology - Quantum Blockchain Nusantara</title>
        <style>
            body { font-family: 'Inter', 'Segoe UI', sans-serif; line-height: 1.8; color: #333; max-width: 1000px; margin: 0 auto; padding: 40px 20px; background: #f0f2f5; }
            .card { background: white; padding: 50px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-top: 8px solid #0d47a1; }
            .header-info { text-align: center; border-bottom: 2px solid #eee; padding-bottom: 30px; margin-bottom: 30px; }
            h1 { color: #0d47a1; margin: 10px 0; font-size: 28px; text-transform: uppercase; letter-spacing: 1px; }
            h2 { color: #1565c0; border-left: 5px solid #0d47a1; padding-left: 15px; margin-top: 40px; font-size: 22px; }
            h3 { color: #333; margin-top: 25px; font-size: 18px; border-bottom: 1px solid #eee; display: inline-block; padding-right: 50px; }
            .step { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
            .step-title { font-weight: bold; color: #0d47a1; display: block; margin-bottom: 10px; font-size: 16px; }
            code { background: #fee2e2; padding: 3px 8px; border-radius: 4px; color: #991b1b; font-family: 'Consolas', monospace; font-size: 0.9em; font-weight: bold; }
            .protocol-box { background: #0f172a; color: #f8fafc; padding: 20px; border-radius: 8px; font-size: 14px; margin: 20px 0; border-left: 5px solid #3fb950; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            table th, table td { text-align: left; padding: 12px; border-bottom: 1px solid #eee; font-size: 14px; }
            table th { background: #f1f5f9; color: #475569; }
            .btn-print { background: #0d47a1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; transition: 0.3s; box-shadow: 0 4px 10px rgba(13,71,161,0.3); }
            .btn-print:hover { background: #1565c0; }
            .footer { margin-top: 60px; text-align: center; color: #64748b; font-size: 13px; border-top: 1px solid #eee; padding-top: 30px; }
            @media print { .btn-print { display: none; } body { background: white; padding: 0; } .card { box-shadow: none; border: none; padding: 0; } }
        </style>
    </head>
    <body>
        <div style="text-align: right; margin-bottom: 20px;">
            <a href="#" onclick="window.print()" class="btn-print">EXPORT TO PDF</a>
        </div>

        <div class="card">
            <div class="header-info">
                <img src="https://raw.githubusercontent.com/kongali1720/QBN/main/logo-coin03.png" width="100" alt="QUANTUM LOGO">
                <h1>Implementation Methodology</h1>
                <p>Quantum Institutional Gateway & Asset Settlement Protocol v0.5.1</p>
                <p style="color: #666; font-style: italic;">Reference: ISO-20022-COMPLIANT-QUANTUM-2026</p>
            </div>

            <h2>I. EXECUTIVE OVERVIEW</h2>
            <p>This document provides the technical framework for Institutional Partners to integrate with the <b>Quantum Blockchain Nusantara Gateway</b>. Our infrastructure facilitates high-velocity settlement across traditional Fiat (SWIFT/RTGS) and Digital Asset (ERC-20/BEP-20) networks.</p>

            <div class="protocol-box">
                <b>SECURITY NOTICE:</b> All requests must be signed with a Bearer Token. System integrity is monitored by <i>Quantum Security Protocol</i>.
            </div>

            <h2>II. CORE INTEGRATION WORKFLOW</h2>
            <div class="step">
                <span class="step-title">PHASE 1: AUTHENTICATION</span>
                Obtain an ephemeral access token by providing credentials to <code>POST /token</code>.
            </div>
            <div class="step">
                <span class="step-title">PHASE 2: ACCOUNT PROVISIONING</span>
                Whitelisting destination accounts via <code>POST /v1/accounts</code>.
            </div>
            <div class="step">
                <span class="step-title">PHASE 3: LIQUIDITY LOCK (QUOTING)</span>
                Lock exchange rates for settlement via <code>POST /v3/profiles/{{id}}/quotes</code>.
            </div>
            <div class="step">
                <span class="step-title">PHASE 4: SETTLEMENT EXECUTION</span>
                Fiat: <code>POST /api/v1/settlement/submit-fiat</code><br>
                Crypto: <code>POST /api/v1/settlement/confirm-crypto</code>
            </div>

            <h2>III. TECHNICAL SPECIFICATIONS</h2>
            <table>
                <tr><th>Standard</th><th>Requirement</th></tr>
                <tr><td>ISO Messaging</td><td>ISO 20022 Compliant</td></tr>
                <tr><td>Security</td><td>TLS 1.2+, Bearer Auth</td></tr>
                <tr><td>Signatory</td><td>QUANTUM ADMINISTRATION</td></tr>
            </table>

            <div class="footer">
                <p><b>Official Institution:</b> QUANTUM BLOCKCHAIN NUSANTARA</p>
                <p>Website: <a href="https://quantumblockchainnusantara.com" target="_blank">quantumblockchainnusantara.com</a> | © 2026</p>
            </div>
        </div>
    </body>
    </html>
    """

# --- INSTITUTIONAL PROTOCOL ---
@app.get("/v2/profiles", tags=["Institutional Protocol"])
async def get_profiles(token: str = Depends(oauth2_scheme)):
    return [{"id": 888168, "type": "institutional", "name": "QUANTUM MASTER ADMIN"}]

@app.get("/v1/accounts", tags=["Institutional Protocol"])
async def get_accounts(currency: str = Query(...), token: str = Depends(oauth2_scheme)):
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                txs = json.load(f)
                return [t["data"] for t in txs if t.get("action") == "ACCOUNT_CREATED" and t["data"]["currency"] == currency]
            except: return []
    return []

@app.post("/v1/accounts", tags=["Institutional Protocol"])
async def create_account(data: RecipientAccount, token: str = Depends(oauth2_scheme)):
    res = data.dict(); res["id"] = int(datetime.now().timestamp())
    save_to_db({"action": "ACCOUNT_CREATED", "data": res}); return res

@app.post("/v3/profiles/{profile_id}/quotes", tags=["Institutional Protocol"])
async def create_quote(profile_id: int, data: QuoteRequest, token: str = Depends(oauth2_scheme)):
    return {"id": str(uuid.uuid4()), "profile": profile_id, "targetAmount": data.targetAmount, "status": "READY"}

@app.post("/v1/transfers", tags=["Institutional Protocol"])
async def make_transfer(data: TransferRequest, token: str = Depends(oauth2_scheme)):
    res = {"id": int(datetime.now().timestamp()), "status": "PROCESSING", "customerTransactionId": data.customerTransactionId}
    save_to_db({"action": "TRANSFER_INIT", "data": res}); return res

@app.post("/v3/profiles/{profile_id}/transfers/{transfer_id}/payments", tags=["Institutional Protocol"])
async def fund_transfer(profile_id: int, transfer_id: int, data: FundTransferRequest, token: str = Depends(oauth2_scheme)):
    return JSONResponse(status_code=201, content={"status": "COMPLETED", "data": {"status": "COMPLETED"}})

# --- SETTLEMENT ASSETS ---
@app.post("/api/v1/settlement/confirm-crypto", tags=["Settlement Assets"])
async def confirm_crypto(data: CryptoConfirmation, token: str = Depends(oauth2_scheme)):
    tx_id = f"QBN-CRYPTO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    save_to_db({"id": tx_id, "type": "CRYPTO", "details": data.dict()}); return {"status": "SUCCESS", "transaction_id": tx_id}

@app.post("/api/v1/settlement/submit-fiat", tags=["Settlement Assets"])
async def submit_fiat(data: FiatTransfer, token: str = Depends(oauth2_scheme)):
    tx_id = f"QBN-FIAT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    save_to_db({"id": tx_id, "type": "FIAT", "details": data.dict()}); return {"status": "SUCCESS", "transaction_id": tx_id}

@app.post("/api/v1/settlement/process-card", tags=["Settlement Assets"])
async def process_card(data: CardTransaction, token: str = Depends(oauth2_scheme)):
    tx_id = f"QBN-VISA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    save_to_db({"id": tx_id, "type": "VISA_CARD", "details": data.dict()}); return {"status": "SUCCESS", "transaction_id": tx_id}

@app.post("/api/v1/settlement/vmml-institutional", tags=["Settlement Assets"])
async def process_vmml(data: VmmlTransaction, token: str = Depends(oauth2_scheme)):
    tx_id = f"QBN-VMML-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    save_to_db({"id": tx_id, "type": "VMML", "details": data.dict()}); return {"status": "SUCCESSFULLY REDEEMED", "transaction_id": tx_id, "auth_code": "8026"}

@app.post("/gateway/integration/remittances", tags=["Institutional Protocol"])
async def create_remittance(data: CreateRemittanceRequest, token: str = Depends(oauth2_scheme)):
    tx_id = str(uuid.uuid4())
    res = {"transactionId": tx_id, "status": "COMPLETED", "details": f"Sending to {data.receiverDetails.accountNumber}"}
    save_to_db({"action": "REMITTANCE_CREATED", "data": res, "input": data.dict()}); return res

# --- SYSTEM ---
@app.get("/api/v1/settlement/history", tags=["System"])
async def get_history(token: str = Depends(oauth2_scheme)):
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try: return json.load(f)
            except: return []
    return []

@app.post("/token", tags=["System"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if USER_DATA.get(form_data.username) == form_data.password:
        return {"access_token": "Token", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid Credentials")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
