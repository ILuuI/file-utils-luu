import time

def timer(function, *args, **kargs):
    """
    Permite cronometrar cuanto tarda una función en ejecutarse e imprime el tiempo en minutos.
    
    :param function: Función a cronometrar.
    :param 'args','kargs': Argumentos de la función.
    """
    start = time.perf_counter()
    function(*args, **kargs)
    finish = time.perf_counter()
    minutes = (finish - start)/60
    return print(f"Tiempo de ejecución: {minutes:.4f} m.")