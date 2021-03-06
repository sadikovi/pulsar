#!/usr/bin/env python

# import libs
import unittest
import random
import sys
from types import IntType, DictType, ListType, StringType, FloatType
# import classes
import analytics.utils.misc as misc
import analytics.exceptions.exceptions as ex
from analytics.core.dataitem import DataItem
from analytics.core.cluster import Cluster
from analytics.core.element import Element
import analytics.algorithms.rank as rank
from analytics.core.attribute.feature import Feature
from analytics.core.attribute.dynamic import Dynamic
from analytics.core.pulse import Pulse, StaticPulse, DynamicPulse


# some general input to test
general_input = [
    None, True, False, sys.maxint, -sys.maxint-1, {}, [],
    {"1": 1, "2": 2}, [1, 2, 3, 4, 5], "abc", 0, 1, -1, 1.233,
    -3.343, 0.23435, " string ", " test test test ", "1"
]


class DataItem_TestSequence(unittest.TestCase):
    def setUp(self):
        self._iterations = 20
        self._teststr = "test string"

    def test_dataitem_init(self):
        for it in range(self._iterations):
            # generate random attributes
            name = random.choice(general_input)
            desc = random.choice(general_input)
            rawseed = random.choice(general_input)
            rawseed = rawseed if rawseed is not None else self._teststr
            seed = str(rawseed).strip() if rawseed is not None else None
            # create and test data item
            d = DataItem(name, desc, rawseed)
            id = misc.generateId(seed)
            self.assertEqual(d._id, id)
            self.assertEqual(d._name, str(name).strip())
            self.assertEqual(d._desc, str(desc).strip())

    def test_dataitem_id(self):
        for it in range(self._iterations):
            rawseed = random.choice(general_input)
            rawseed = rawseed if rawseed is not None else self._teststr
            d = DataItem(self._teststr, self._teststr, rawseed)
            seed = str(rawseed).strip() if rawseed is not None else None
            id = misc.generateId(seed)
            self.assertEqual(d.id(), id)

    def test_dataitem_name(self):
        for it in range(self._iterations):
            name = random.choice(general_input)
            d = DataItem(name, self._teststr, None)
            self.assertEqual(d.name(), str(name).strip())

    def test_dataitem_desc(self):
        for it in range(self._iterations):
            desc = random.choice(general_input)
            d = DataItem(self._teststr, desc, None)
            self.assertEqual(d.desc(), str(desc).strip())

    def test_dataitem_getJSON(self):
        for it in range(self._iterations):
            # generate random attributes
            name = random.choice(general_input)
            desc = random.choice(general_input)
            rawseed = random.choice(general_input)
            rawseed = rawseed if rawseed is not None else self._teststr
            seed = str(rawseed).strip() if rawseed is not None else None
            # create and test data item json object
            d = DataItem(name, desc, seed)
            obj = d.getJSON()
            id = misc.generateId(seed)
            self.assertEqual(type(obj), DictType)
            self.assertEqual(obj["id"], id)
            self.assertEqual(obj["name"], str(name).strip())
            self.assertEqual(obj["desc"], str(desc).strip())


class Cluster_TestSequence(unittest.TestCase):
    def setUp(self):
        self._iterations = 20
        self._teststr = "test string"
        self._parentSeq = [
            None,
            Cluster(None, self._teststr, self._teststr),
            DataItem(self._teststr, self._teststr)
        ]

    def test_cluster_init(self):
        # test iterations
        for it in range(self._iterations):
            for parent in self._parentSeq:
                # generate random attributes
                id = str(random.choice(general_input)).strip()
                name = random.choice(general_input)
                desc = random.choice(general_input)
                seed = random.choice(general_input)
                # create and test cluster
                if parent is not None and type(parent) is not Cluster:
                    with self.assertRaises(ex.AnalyticsCheckError):
                        d = Cluster(id, name, desc, parent)
                else:
                    d = Cluster(id, name, desc, parent)
                    self.assertEqual(d._id, misc.generateId(id))
                    self.assertEqual(d._name, str(name).strip())
                    self.assertEqual(d._desc, str(desc).strip())
                    self.assertEqual(d._parent, parent)
                    self.assertEqual(d._children, {})

    def test_cluster_initUniqueId(self):
        for it in range(self._iterations):
            # as random input can be None, id will be random
            id = str(random.choice(general_input)).strip()
            name = random.choice(general_input)
            desc = random.choice(general_input)
            cl1 = Cluster(id, name, desc)
            cl2 = Cluster(id, name, desc)
            # check that they have the same ids
            self.assertEqual(cl1.id(), cl2.id())

    def test_cluster_parent(self):
        for parent in self._parentSeq:
            if parent is None or type(parent) is Cluster:
                d = Cluster(self._teststr, self._teststr, self._teststr, parent)
                self.assertEqual(d.parent(), parent)
            else:
                with self.assertRaises(ex.AnalyticsCheckError):
                    d = Cluster(
                        self._teststr,
                        self._teststr,
                        self._teststr,
                        parent
                    )

    def test_cluster_children(self):
        # quite simple test
        d = Cluster(self._teststr, self._teststr, self._teststr)
        self.assertEqual(type(d.children()), ListType)
        self.assertEqual(d.children(), [])

    def test_cluster_isLeaf(self):
        # quite simple test
        d = Cluster(self._teststr, self._teststr, self._teststr)
        self.assertEqual(d.isLeaf(), True)

    def test_cluster_setParent(self):
        for parent in self._parentSeq:
            d = Cluster(self._teststr, self._teststr, self._teststr)
            self.assertEqual(d.parent(), None)
            if parent is None or type(parent) is Cluster:
                d.setParent(parent)
                self.assertEqual(d.parent(), parent)
            else:
                with self.assertRaises(ex.AnalyticsCheckError):
                    d.setParent(parent)

    def test_cluster_makeLeaf(self):
        # create cluster
        d = Cluster(self._teststr, self._teststr, self._teststr)
        # check leaf
        self.assertEqual(d.isLeaf(), True)
        # assign some info
        d._children["test"] = "string"
        self.assertEqual(d.isLeaf(), False)
        # make it leaf
        d.makeLeaf()
        self.assertEqual(d.isLeaf(), True)
        self.assertEqual(d._children, {})

    def test_cluster_addChild(self):
        # create parent cluster and child cluster
        parent = Cluster(self._teststr, self._teststr, self._teststr)
        for it in range(self._iterations):
            name = random.choice(general_input)
            desc = random.choice(general_input)
            children = [
                None,
                parent,
                Cluster(None, name, desc),
                DataItem(name, desc)
            ]
            for child in children:
                if type(child) is not Cluster:
                    with self.assertRaises(ex.AnalyticsCheckError):
                        parent.addChild(child)
                elif child.id() == parent.id():
                    with self.assertRaises(ex.AnalyticsStandardError):
                        parent.addChild(child)
                else:
                    parent.addChild(child)
        # number of children (theoretically):
        num = self._iterations
        self.assertEqual(len(parent.children()), num)

    def test_cluster_removeChild(self):
        parent = Cluster(self._teststr, self._teststr, self._teststr)
        for it in range(self._iterations):
            name = random.choice(general_input)
            desc = random.choice(general_input)
            # prepare children
            children = [
                None,
                parent,
                Cluster(None, name, desc),
                DataItem(name, desc)
            ]
            for child in children:
                # check type of the child
                if type(child) is not Cluster:
                    with self.assertRaises(ex.AnalyticsCheckError):
                        parent.addChild(child)
                elif child.id() == parent.id():
                    with self.assertRaises(ex.AnalyticsStandardError):
                        parent.addChild(child)
                else:
                    parent.addChild(child)
                parent.removeChild(child)
            self.assertEqual(parent.children(), [])
        self.assertEqual(parent.children(), [])

    def test_cluster_getJSON(self):
        for it in range(self._iterations):
            id = random.choice(general_input)
            name = random.choice(general_input)
            desc = random.choice(general_input)
            parents = [None, Cluster(id, name, desc)]
            for parent in parents:
                cl = Cluster(
                    self._teststr,
                    self._teststr,
                    self._teststr,
                    parent
                )
                obj = cl.getJSON()
                pid = None if parent is None else parent.id()
                self.assertEqual(obj["id"], cl.id())
                self.assertEqual(obj["name"], cl.name())
                self.assertEqual(obj["desc"], cl.desc())
                self.assertEqual(obj["parent"], pid)
                # has to be equal to empty array for this case
                self.assertEqual(obj["children"], [])


class Element_TestSequence(unittest.TestCase):
    def setUp(self):
        self._iterations = 20
        self._teststr = "test string"
        self._clusters = [
            None,
            Cluster(self._teststr, self._teststr, self._teststr),
            DataItem(self._teststr, self._teststr),
            sys.maxint,
            -sys.maxint-1
        ]
        self._ranks = [
            None,
            rank.RSYS.UND_RANK,
            sys.maxint,
            -sys.maxint-1
        ]
        self._features = [
            None,
            sys.maxint,
            -sys.maxint-1,
            Feature(self._teststr, self._teststr, self._teststr)
        ]

    def test_element_init(self):
        for it in range(self._iterations):
            id = str(random.choice(general_input)).strip()
            name = random.choice(general_input)
            desc = random.choice(general_input)
            cluster = random.choice(self._clusters)
            r = random.choice(self._ranks)
            if cluster is not None and type(cluster) is not Cluster:
                with self.assertRaises(ex.AnalyticsCheckError):
                    el = Element(id, name, desc, cluster, r)
            elif type(r) is not rank.Rank:
                with self.assertRaises(ex.AnalyticsCheckError):
                    el = Element(id, name, desc, cluster, r)
            else:
                el = Element(id, name, desc, cluster, r)
                self.assertEqual(el.id(), misc.generateId(id))
                self.assertEqual(el.name(), str(name).strip())
                self.assertEqual(el.desc(), str(desc).strip())
                self.assertEqual(el._cluster, cluster)
                self.assertEqual(el._rank, r)
                self.assertEqual(el._features, {})

    def test_element_cluster(self):
        for cluster in self._clusters:
            if cluster is None or type(cluster) is Cluster:
                el = Element(None, self._teststr, self._teststr, cluster)
                self.assertEqual(el.cluster(), cluster)
            else:
                with self.assertRaises(ex.AnalyticsCheckError):
                    el = Element(None, self._teststr, self._teststr, cluster)

    def test_element_rank(self):
        for r in self._ranks:
            if type(r) is rank.Rank:
                el = Element(None, self._teststr, self._teststr, None, r)
                self.assertEqual(el.rank(), r)
            else:
                with self.assertRaises(ex.AnalyticsCheckError):
                    el = Element(None, self._teststr, self._teststr, None, r)

    def test_element_features(self):
        el = Element(None, self._teststr, self._teststr)
        self.assertEqual(el.features(), [])

    def test_element_addFeature(self):
        el = Element(None, self._teststr, self._teststr)
        for feature in self._features:
            if type(feature) is Feature:
                el.addFeature(feature)
                self.assertEqual(el.features(), [feature])
            else:
                with self.assertRaises(ex.AnalyticsCheckError):
                    el.addFeature(feature)

    def test_element_addFeatures(self):
        el = Element(None, self._teststr, self._teststr)
        with self.assertRaises(ex.AnalyticsCheckError):
            el.addFeatures(self._features)
        # create new list of features
        features = [
            Feature("#1", self._teststr, self._teststr),
            Feature("#2", self._teststr, self._teststr),
        ]
        el.addFeatures(features)
        self.assertEqual(len(el.features()), len(features))
        # sorted list of features ids
        featuresIds = sorted([a.id() for a in features])
        self.assertEqual(sorted(el._features.keys()), featuresIds)

    def test_element_getJSON(self):
        # initialise clusers and ranks
        clusters = [None, Cluster(None, self._teststr, self._teststr)]
        ranks = [None, rank.RSYS.UND_RANK]
        for it in range(self._iterations):
            clr = random.choice(clusters)
            rnk = random.choice(ranks)
            if rnk is None:
                with self.assertRaises(ex.AnalyticsCheckError):
                    el = Element(None, self._teststr, self._teststr, clr, rnk)
                continue
            el = Element(None, self._teststr, self._teststr, clr, rnk)
            obj = el.getJSON()
            self.assertEqual(obj["cluster"], None if clr is None else clr.id())
            self.assertEqual(obj["rank"], None if rnk is None else rnk.getJSON())
            self.assertEqual(obj["features"], [])


class Pulse_TestSequence(unittest.TestCase):
    def setUp(self):
        self._iterations = 20
        self._teststr = "test string"

    def test_pulse_init(self):
        for it in range(self._iterations):
            # generate attributes
            name = random.choice(general_input)
            desc = random.choice(general_input)
            sample = random.choice(general_input)
            seed = str(name).strip() + type(sample).__name__
            # create pulse instance
            pulse = Pulse(name, desc, sample)
            self.assertEqual(pulse.id(), misc.generateId(seed))
            self.assertEqual(pulse.name(), str(name).strip())
            self.assertEqual(pulse.desc(), str(desc).strip())
            self.assertEqual(pulse._type, type(sample))
            self.assertEqual(len(pulse._store), len(set()))
            self.assertEqual(pulse._default, None)

    def test_pulse_type(self):
        for sample in general_input:
            pulse = Pulse(self._teststr, self._teststr, sample)
            self.assertEqual(pulse.type(), type(sample))

    def test_pulse_store(self):
        pulse = Pulse(self._teststr, self._teststr, self._teststr)
        self.assertEqual(len(pulse.store()), len(set()))

    def test_pulse_default(self):
        pulse = Pulse(self._teststr, self._teststr, self._teststr)
        self.assertEqual(pulse.default(), None)

    def test_pulse_addValueToStore(self):
        samples = [1, "1", 1.0]
        for sample in samples:
            testset = set()
            pulse = Pulse(self._teststr, self._teststr, sample)
            for it in range(self._iterations):
                value = random.choice(general_input)
                pulse.addValueToStore(value)
                if type(value) == type(sample):
                    testset.add(value)
            self.assertEqual(len(pulse.store()), len(testset))

    def test_pulse_getJSON(self):
        for sample in general_input:
            pulse = Pulse(self._teststr, self._teststr, sample)
            obj = pulse.getJSON()
            self.assertEqual(obj["type"], pulse.type().__name__)
            self.assertEqual(obj["default"], pulse.default())

    def test_pulse_static(self):
        for sample in general_input:
            pulse = Pulse(self._teststr, self._teststr, sample)
            # pulse static property is always static
            self.assertEqual(pulse.static(), True)


class StaticPulse_TestSequence(unittest.TestCase):
    def setUp(self):
        self._iterations = 20
        self._sample = 1
        self._teststr = "test string"

    def test_staticpulse_setDefaultValue(self):
        test_sample = 1
        pulse = StaticPulse(self._teststr, self._teststr, self._sample)
        for value in general_input:
            pulse.addValueToStore(value)
        test_default = None
        # go through general input
        for default in general_input:
            if default is None or type(default) is type(self._sample):
                test_default = default
                pulse.setDefaultValue(default)
            self.assertEqual(pulse.default(), test_default)

    def test_staticpulse_static(self):
        pulse = StaticPulse(self._teststr, self._teststr, self._sample)
        self.assertEqual(pulse.static(), True)


class DynamicPulse_TestSequence(unittest.TestCase):
    def setUp(self):
        self._iterations = 20
        self._sample = 117.0
        self._prior = Dynamic.ForwardPriority
        self._teststr = "test string"

    def test_dynamicpulse_setDefaultValue_static(self):
        # test staticly behaving dynamic pulse
        pulse = DynamicPulse(self._teststr, self._teststr,
                                self._sample, self._prior, True)
        for value in general_input:
            pulse.addValueToStore(value)
        # add sample parameter
        updated_list = general_input
        updated_list.append(self._sample)
        test_default = None
        # go through values of updated list
        for default in updated_list:
            pulse.setDefaultValue(default)
            if default is None:
                test_default = default
            elif type(default)==type(self._sample) and default in pulse.store():
                test_default = default
            self.assertEqual(pulse.default(), test_default)

    def test_dynamicpulse_setDefaultValue_dynamic(self):
        # test fully dynamic pulse
        pulse = DynamicPulse(self._teststr, self._teststr,
                                self._sample, self._prior, False)
        for value in general_input:
            pulse.addValueToStore(value)
        # add sample parameter
        updated_list = general_input
        updated_list.append(self._sample)
        test_default = None
        for default in general_input:
            # must assign value without checking in the store
            if default is None:
                if pulse._store is not None:
                    s = sum(pulse._store); n = len(pulse._store)
                    if pulse._type is IntType:
                        test_default = int(s*1.0/n)
                    elif pulse._type is FloatType:
                        test_default = round(s*1.0/n, 2)
                    else:
                        test_default = None
                else:
                    test_default = None
            elif type(default) == type(self._sample):
                test_default = default
            pulse.setDefaultValue(default)
            self.assertEqual(pulse.default(), test_default)

    def test_dynamicpulse_static(self):
        pulse = DynamicPulse(self._teststr, self._teststr,
                                self._sample, self._prior, False)
        self.assertEqual(pulse.static(), False)
        pulse = DynamicPulse(self._teststr, self._teststr,
                                self._sample, self._prior, True)
        self.assertEqual(pulse.static(), True)

    def test_dynamicpulse_setStatic(self):
        pulse = DynamicPulse(self._teststr, self._teststr,
                                self._sample, self._prior, False)
        self.assertEqual(pulse.static(), False)
        pulse.setStatic(True)
        self.assertEqual(pulse.static(), True)
        pulse.setStatic([])
        self.assertEqual(pulse.static(), False)
        pulse.setStatic(1)
        self.assertEqual(pulse.static(), True)

    def test_dynamicpulse_changeDefault(self):
        # sample of data and maximum elements in range
        sample = 1; max_el = 5
        pulse = DynamicPulse(self._teststr, self._teststr,
                                sample, self._prior, False)
        self.assertEqual(pulse.default(), None)
        for i in range(max_el):
            pulse.addValueToStore(i)
        default = int(sum(range(max_el))*1.0 / len(range(max_el)))
        self.assertEqual(pulse.default(), default)
        # set default that out of range
        pulse.setDefaultValue(max_el*2)
        self.assertEqual(pulse.default(), max_el*2)
        # change static attribute to True
        pulse.setStatic(True)
        self.assertEqual(pulse.default(), None)
        pulse.setStatic(False)
        # after reseting to dynamic default value should not be None
        self.assertEqual(pulse.default(), default)

    def test_dynamicpulse_floatDefault(self):
        elems = [320.0, 300.0, 199.0, 234.0, 250.0, 245.0, 230.0]
        avg = sum(elems)*1.0 / len(elems)
        # round average
        avg = int(avg*100)*1.0 / 100
        pulse = DynamicPulse(
            self._teststr,
            self._teststr,
            elems[0],
            self._prior
        )
        for elem in elems:
            pulse.addValueToStore(elem)
        self.assertEqual(pulse.default(), avg)

# Load test suites
def _suites():
    return [
		DataItem_TestSequence,
		Cluster_TestSequence,
		Element_TestSequence,
		Pulse_TestSequence,
		StaticPulse_TestSequence,
		DynamicPulse_TestSequence
    ]

# Load tests
def loadSuites():
    # global test suite for this module
    gsuite = unittest.TestSuite()
    for suite in _suites():
        gsuite.addTest(unittest.TestLoader().loadTestsFromTestCase(suite))
    return gsuite

if __name__ == '__main__':
    suite = loadSuites()
    print ""
    print "### Running tests ###"
    print "-" * 70
    unittest.TextTestRunner(verbosity=2).run(suite)
