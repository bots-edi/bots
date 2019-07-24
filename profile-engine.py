#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == "__main__":
    import cProfile

    cProfile.run("from bots import engine; engine.start()", "profile.tmp")
    import pstats

    p = pstats.Stats("profile.tmp")
    # ~ p.sort_stats('cumulative').print_stats(25)
    p.sort_stats("time").print_stats(50)
    # ~ p.print_callees('deepcopy').print_stats(1)
    p.print_callees("mydeepcopy")
    # ~ p.sort_stats('time').print_stats('grammar.py',50)
