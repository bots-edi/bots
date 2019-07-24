import ConfigParser

config = ConfigParser.ConfigParser()

config.read(r"/usr/local/lib/python2.7/dist-packages/bots/config/bots.ini")
config.set("jobqueue", "enabled", "True")
config.set("dirmonitor1", "path", "/dirmon")
config.remove_section("dirmonitor2")
with open(
    r"/usr/local/lib/python2.7/dist-packages/bots/config/bots.ini", "wb"
) as configfile:
    config.write(configfile)
