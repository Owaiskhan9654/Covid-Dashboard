from pyngrok import ngrok

# open a http tunnel on the default port 80
ssh_url = ngrok.connect(22, 'tcp')
public_url = ngrok.connect(host="0.0.0.0",port=80,)
print(public_url)
# open a ssh tunnel
#ngrok http -host-header=localhost 8080
#http://localhost:4040/status