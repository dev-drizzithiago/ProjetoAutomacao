import speedtest


servidor_teste = st.get_best_server()['name']

teste_upload = f'{st.upload() / 1_000_000:.2f} mbps'
teste_ping = f'{st.results.ping} ms'

print(servidor_teste)

print(teste_download)
print(teste_upload)
print(teste_ping)
