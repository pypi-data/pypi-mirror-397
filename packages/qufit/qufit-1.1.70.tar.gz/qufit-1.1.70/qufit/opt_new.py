import functools
import skopt, pickle
import numpy as np
from tqdm.notebook import trange

def parameter_filter(x, dec=None, high=None, low=None):
    if dec is not None:
        x = np.asarray([np.round(a, decimals=d) for a, d in zip(x, dec)])
    if high is None and low is None:
        return x
    return x.clip(low, high)

def minimize_bayes(target,
             start,
             senstive=None,
             dec=None,
             high=None,
             low=None,
             kws = {},
             print_info=False,
             n_iter=25,
             n_jobs = 10,
             model_queue_size = 1,
             initOptclass = None,
             peak = None,
             pbar = True):
    
#     @functools.lru_cache()
#     def cache_target(*x):
#         return target(*x,**kws)
    low = np.asarray([np.round(float(a), decimals=d) for a, d in zip(low, dec)])
    high = np.asarray([np.round(float(a), decimals=d) for a, d in zip(high, dec)])
    
    if initOptclass is None:
        opt = skopt.Optimizer(list(zip(low,high)),n_jobs=n_jobs,model_queue_size=model_queue_size) 
    else:
        opt = initOptclass
    
    y = target(start,**kws)
    ymin = y
    opt.tell(list(start),y)
    print(f'x0={list(start)},y0={y}')

    scan_iter = trange(n_iter,desc=f'Optimizing {target.__name__}') if pbar and not print_info else range(n_iter)
    
    for i in scan_iter:
        x = opt.ask()
        x = parameter_filter(x, dec, high, low)
        y = target(x,**kws)
        opt.tell(list(x),y)
        if print_info:
            if y > ymin:
                print(f'step{i+1},  x={list(x)},  y={y}')
            else:
                ymin = y
                pp_info = f'step{i+1},  x={list(x)},  y={y}'
                print(f"\033[1;30;41m{pp_info}\033[0m")
        
        if peak is not None and y <= peak:
            return opt
        
    return opt