import cProfile
# python -m cProfile -o profile.stats script.py
# python -m pstats profile.stats
# # Profile just this specific function call
#    cProfile.run('my_function()')
#    results = pstats.Stats(cProfile.Profile())
#    results.sort_stats(pstats.SortKey.TIME)
# can use tuna to visualize


# py-spyrun -p $PID --duration 60 ??? --format raw

def bpe_example():
    