#!/usr/bin/env python

# import classes
from analytics.core.dataitem import DataItem
from analytics.core.attribute.dynamic import Dynamic


class Pulse(DataItem):
    """
        Pulse class core filtering element in analytics, keeps values of
        features and type. It allows static or dynamic filtering. Type is a
        simple type, not a data structure, e.g. StringType, IntType or
        FloatType that are hashable.

        Attributes:
            _type (Type): feature type (data type)
            _store (Set<obj>): set of feature values
            _default (obj): default value
    """
    def __init__(self, name, desc, sample):
        seed = str(name).strip() + type(sample).__name__
        super(Pulse, self).__init__(name, desc, seed)
        self._type = type(sample)
        self._store = set()
        self._default = None

    # [Public]
    def type(self):
        """
            Returns Pulse feature type.

            Returns:
                Type: Pulse feature type
        """
        return self._type

    # [Public]
    def store(self):
        """
            Returns list of values in store.

            Returns:
                list<obj>: list of values
        """
        return list(self._store)

    # [Public]
    def default(self):
        """
            Returns current default value.

            Returns:
                obj: default value
        """
        return self._default

    # [Public]
    def addValueToStore(self, value):
        """
            Adds value to store of the static pulse.

            Args:
                value (obj): value for the pulse
        """
        if type(value) is self._type:
            self._store.add(value)

    # [Public]
    def getJSON(self):
        """
            Returns json representation of the instance.

            Returns:
                dict<str, obj>: json representation of the instance
        """
        obj = super(Pulse, self).getJSON()
        obj["type"] = self._type
        obj["default"] = self._default
        return obj


class StaticPulse(Pulse):
    """
        StaticPulse is class for static properties that do not change over time.
        Standard filtering option. Cannot mimic behaviour of dynamic pulse.
    """
    def __init__(self, name, desc, sample):
        super(StaticPulse, self).__init__(name, desc, sample)

    # [Public]
    def setDefaultValue(self, default):
        """
            Sets default value for StaticPulse instance. Checks that default
            value is in store, and assigns new value, otherwise action is
            skipped.

            Args:
                default (obj): default value
        """
        if type(default) is self._type and default in self._store:
            self._default = default


class DynamicPulse(Pulse):
    """
        DynamicPulse is class for dynamic properties that do change over time.
        Can mimic StandardPulse. Usual filtering does not apply for dynamic
        pulse.

        Attributes:
            _static (bool): shows currently selected mode
            _dynamic (Dynamic): dynamic attribute
    """
    def __init__(self, name, desc, sample, priority, static=False):
        super(DynamicPulse, self).__init__(name, desc, sample)
        self._static = static
        self._dynamic = Dynamic(priority)

    # [Public]
    def setDefaultValue(self, default):
        """
            Sets default value for DynamicPulse instance.

            Args:
                default (obj): default value
        """
        if type(default) is self._type:
            if static:
                self._default = default
            # if dynamic property is mimicking static pulse, check store
            elif default in self._store:
                self._default = default
