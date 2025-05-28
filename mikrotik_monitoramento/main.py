
import mikrotik_logs

if __name__ == '__main__':
    iniciando_obj = mikrotik_logs.BuscandoLogsMikrotik()
    logs = iniciando_obj.log_dhcp()
    for log in logs:
        print(log)