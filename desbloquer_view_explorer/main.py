
import re
from pathlib import Path

home_usuario = Path.home()

comando_powershell = "Get-ChildItem -Path . -Recurse | Unblock-File "

result_comando = os.run()

