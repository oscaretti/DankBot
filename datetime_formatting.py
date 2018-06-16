import datetime


def read_timedelta(args):
    keys = ["D", "M", "S"]
    units = {key: 0 for key in keys}
    for arg in args:
        units[arg[-1:].upper()] = int(arg[:-1])
    return datetime.timedelta(days=units["D"], minutes=units["M"], seconds=units["S"])


def neat_timedelta(time):
    keys = ["days", "seconds", "microseconds"]
    dsms = str(time).split(sep=":")
    mapped = dict(zip(keys, dsms))
    ret = ""
    for key in keys:
        if int(mapped[key]) != 0:
            ret += "%i %s " % (int(mapped[key]), key)
    ret.strip()
    return ret
