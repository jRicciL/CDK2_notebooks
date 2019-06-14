def find_gaps(seq, r=1): # r es el número de residuos móviles al lado de la ventana del gap
    import re
    '''Encontrar el número e inicio y final de los gaps en el alineamiento
    seq: secuencia '''
    seq_len = len(seq)
    gaps = list(re.finditer('[-]+', seq)) # todas las subsecuencias que tienen uno o más guiones
    num_gaps = len(gaps); gap_lengths = []
    gap_list = []; gap_window = []
    # Obtener el índice de inicio y final del gap
    for i , gap in enumerate(gaps, 1):
        start = gap.start() + 1 # Sumamos uno pues la secuecnia está indexada a partir de 1
        end = gap.end() + 1 # sumamos 1
        gap_lengths.append(end - start + 1)
        gap_list.append([start, end])
        # end_right y start right evitan que la ventana sobrepase la secuencia de
        # la proteína al inicio o al principio
        end_right = end if end >= seq_len else end  + r
        start_right = start if start == 1 else start - r
        gap_window.append([start_right, end_right])
    return({"num_gaps": num_gaps, "gap_lengths":gap_lengths,
            "gap_list": gap_list, "gap_window": gap_window})