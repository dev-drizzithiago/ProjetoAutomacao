import speedtest

st = speedtest.Speedtest()

print(f'{st.download() / 1_000_000:.2f} mbps')
print(f'{st.upload() / 1_000_000:.2f} mbps')
print(f'{st.results.ping} ms')
