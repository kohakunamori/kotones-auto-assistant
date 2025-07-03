from terminal import print_status
from launcher import main_launch

try:
    main_launch()
except KeyboardInterrupt:
    print_status("运行结束", status='info')