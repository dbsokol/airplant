import braintree

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id="r4dzzgf5vsz9643j",
        public_key="6z5x4pm5d7sm3yfc",
        private_key="b0e39319d54b379378f101305e3276e0"
    )
)

client_token = gateway.client_token.generate({
    "customer_id": 842166731
})

@app.route("/client_token", methods=["GET"])
def client_token():
  return gateway.client_token.generate()
  
  