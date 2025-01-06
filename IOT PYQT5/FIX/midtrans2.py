import midtransclient

# Konfigurasi Sandbox (untuk testing)
server_key = "SB-Mid-server-lePt6oLvW_DA8AF3_6VN2gtW"  # Ganti dengan server key sandbox Anda
client_key = "SB-Mid-client-ubIyHs6SerjiaaQe"  # Ganti dengan client key sandbox Anda

# Inisialisasi Snap API Client
snap = midtransclient.Snap(
    is_production=False,  # False untuk Sandbox, True untuk Production
    server_key=server_key,
    client_key=client_key
)



# Data Transaksi Sederhana
transaction_data = {
    "transaction_details": {
        "order_id": "test-order-001",
        "gross_amount": 50000  # Jumlah transaksi dalam IDR
    },
    "credit_card": {
        "secure": True
    }
}

# Test koneksi dengan membuat transaksi
try:
    response = snap.create_transaction(transaction_data)
    print("Connection Successful!")
    print("Transaction Token:", response["token"])
    print("Redirect URL:", response["redirect_url"])
except Exception as e:
    print("Connection Failed!")
    print("Error:", e)
