from collections import defaultdict

from models import Model

# -----------------------------------------------------------------------------
# Packets
# -----------------------------------------------------------------------------


class PacketMeta(type):
    _CLASSES = {}

    @classmethod
    def getClass(cls, dct):
        typeCls = cls._CLASSES[dct['type']]
        if typeCls.__metaclass__ != cls:
            typeCls = typeCls.__metaclass__.getClass(dct)
        return typeCls

    def __new__(cls, name, bases, attrs):
        cls = super(PacketMeta, cls).__new__(cls, name, bases, attrs)
        if cls.TYPE is not None and cls.TYPE not in PacketMeta._CLASSES:
            PacketMeta._CLASSES[cls.TYPE] = cls
        return cls


class Packet(Model):
    __metaclass__ = PacketMeta

    TYPE = None

    @staticmethod
    def parsePacket(dct):
        cls = PacketMeta.getClass(dct)
        packet = cls.new(dct)
        return packet

    def buildPacket(self):
        dct = defaultdict(defaultdict)
        self.build(dct)
        return dct

    def __repr__(self):
        items = ['%s=%s' % item for item in self.__dict__.items()]
        return 'Packet(type=%s, %s)' % (self.TYPE, ', '.join(items))

# -----------------------------------------------------------------------------
# Events
# -----------------------------------------------------------------------------


class EventMeta(PacketMeta):
    _CLASSES = {}

    @classmethod
    def getClass(cls, dct):
        try:
            typeCls = cls._CLASSES[dct['evt_type']]
        except KeyError as e:
            typeCls = GenericEvent
        if typeCls.__metaclass__ != cls:
            typeCls = typeCls.__metaclass__.getClass(dct)
        return typeCls

    def __new__(cls, name, bases, attrs):
        cls = super(EventMeta, cls).__new__(cls, name, bases, attrs)
        if cls.EVT_TYPE is not None and cls.EVT_TYPE not in EventMeta._CLASSES:
            EventMeta._CLASSES[cls.EVT_TYPE] = cls
        return cls


class Event(Packet):
    __metaclass__ = EventMeta

    TYPE = 'event'
    EVT_TYPE = None

    def __init__(self):
        super(Event, self).__init__()
        assert self.EVT_TYPE is not None, "EVT_TYPE not implemented"

    def build(self, dct):
        dct['type'] = self.TYPE
        dct['evt_type'] = self.EVT_TYPE
        self.buildEvent(dct)
        return dct

    def parse(self, dct):
        self.parseEvent(dct)

    def buildEvent(self, dct):
        raise NotImplementedError("buildEvent() not implemented")

    def parseEvent(self, dct):
        raise NotImplementedError("parseEvent() not implemented")

    def __repr__(self):
        items = ['%s=%s' % item for item in self.__dict__.items()]
        return 'Event(type=%s, %s)' % (self.EVT_TYPE, ', '.join(items))

    def __call__(self):
        raise NotImplementedError("__call__() not implemented")


class SimpleEvent(Event):

    def buildEvent(self, dct):
        dct.update(self.__dict__)

    def parseEvent(self, dct):
        self.__dict__.update(dct)


class GenericEvent(Event):

    def buildEvent(self, dct):
        dct.update(self.__dict__)

    def parseEvent(self, dct):
        self.__dict__.update(dct)


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------


class CommandMeta(PacketMeta):
    _CLASSES = {}

    @classmethod
    def getClass(cls, dct):
        typeCls = cls._CLASSES[dct['cmd_type']]
        if typeCls.__metaclass__ != cls:
            typeCls = typeCls.__metaclass__.getClass(dct)
        return typeCls

    def __new__(cls, name, bases, attrs):
        cls = super(CommandMeta, cls).__new__(cls, name, bases, attrs)
        if cls.CMD_TYPE is not None \
                and cls.CMD_TYPE not in CommandMeta._CLASSES:
            CommandMeta._CLASSES[cls.CMD_TYPE] = cls
        return cls


class Command(Packet):
    __metaclass__ = CommandMeta

    TYPE = 'cmd'
    CMD_TYPE = None

    def __init__(self):
        super(Command, self).__init__()
        assert self.CMD_TYPE is not None, "CMD_TYPE not implemented"

    def build(self, dct):
        dct['type'] = self.TYPE
        dct['cmd_type'] = self.CMD_TYPE
        self.buildCommand(dct)
        return dct

    def parse(self, dct):
        self.parseCommand(dct)

    def buildCommand(self, dct):
        raise NotImplementedError("buildCommand() not implemented")

    def parseCommand(self, dct):
        raise NotImplementedError("parseCommand() not implemented")

    def __repr__(self):
        items = ['%s=%s' % item for item in self.__dict__.items()]
        return 'Command(type=%s, %s)' % (self.CMD_TYPE, ', '.join(items))


class SimpleCommand(Command):

    def buildCommand(self, dct):
        dct.update(self.__dict__)

    def parseCommand(self, dct):
        self.__dict__.update(dct)

# -----------------------------------------------------------------------------
# Queries
# -----------------------------------------------------------------------------


class Query(object):
    CALLBACKS = []

    @classmethod
    def registerCallback(cls, d):
        cls.CALLBACKS.append(d)

# -----------------------------------------------------------------------------
# Replies
# -----------------------------------------------------------------------------


class Reply(object):
    QUERY = None

    def __init__(self):
        super(Reply, self).__init__()
        assert self.QUERY is not None, "QUERY not implemented"

    def triggerCallback(self):
        d = self.QUERY.CALLBACKS.pop()
        d.callback(self)

# -----------------------------------------------------------------------------
# Container
# -----------------------------------------------------------------------------


class Container(Model):

    def build(self, dct):
        super(Container, self).build(dct)
        dct['__size__'] = len(self._content)
        return dct

    def parse(self, dct):
        self.size = dct['__size__']
        super(Container, self).parse(dct)

    def getContent(self):
        return self._content

    def setContent(self, content):
        self._content = content