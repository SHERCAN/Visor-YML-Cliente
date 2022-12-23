import multiprocessing
import uvicorn
from config.var_env import mode

if __name__ == '__main__':
    multiprocessing.freeze_support()
    if mode == 'TEST':
        uvicorn.run('app:app', port=8080, reload=True)# log_level='trace', access_log=True,
    else:
        uvicorn.run(app='app:app', host='0.0.0.0', port=8080,
                    log_level='info', access_log=False)