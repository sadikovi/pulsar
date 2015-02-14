# import libs
from types import ListType
# import classes
import analytics.datavalidation.group as g
import analytics.exceptions.checkerror as c


class GroupsMap(object):
    """
        GroupsMap class helps to consolidate and maintain groups. Each group
        can be easily found by it's guid or external id (using _guidmap).
        GroupsMap also helps to build hierarchy from the groups provided.

        _map is dictionary to hold pairs {guid, group}, where @guid (key) is an
        internal id of the Group object, and @group (value) is a reference to
        that Group object.

        _guidmap is dictionary to hold pairs {externalId, guid}, where
        externalId is an external id of the Group object and guid is an
        internal id of the same object. In case if there are two groups with
        the same external id, _guidmap will have only one pair to reference
        the last object. Usually, it is used to exchange parent external ids
        with new guids.

        Attributes:
            _map (dict<str, Group>)     : dict to hold pairs {guid, group}
            _guidmap (dict<str, str>)   : dict to hold pairs {externalId, guid}
    """

    def __init__(self):
        self.reset()

    # [Public]
    def reset(self):
        """
            Resets all the attributes of the instance to the empty
            dictionaries. Useful, if GroupsMap instance is intended to be
            reusable.
        """
        self._map = {}
        self._guidmap = {}

    # [Public]
    def has(self, id):
        """
            Checks if group with id provided is in groupsmap instance. It uses
            guid to reference _map attribute. Returns True, if group is in _map
            dictionary, and False otherwise.

            Args:
                id (str): group's guid to check if group is in Groupsmap

            Returns:
                bool: indicator whether group is in _map or not
        """
        return True if id is not None and id in self._map else False

    # [Public]
    def assign(self, group):
        """
            Adds group to the groupsmap. Group has to be a Group instance.
            If groupsmap already has this group, action is ignored. Otherwise,
            group is added to groupsmap.

            Args:
                group (Group): to be added to the groupsmap
        """
        if type(group) is not g.Group:
            raise c.CheckError("<type 'Group'>", str(type(group)))
        if self.has(group.getId()) is False:
            self._map[group.getId()] = group
            self._guidmap[group.getExternalId()] = group.getId()

    # [Public]
    def remove(self, id):
        """
            Removes group from groupsmap by id provided. Id is internal guid.
            If groupsmap does not have id as a key, action is ignored.
            Otherwise, group is removed from groupsmap.

            Args:
                id (str): a group's guid
        """
        if self.has(id):
            group = self._map[id]
            del self._map[id]
            self._guidmap[group.getExternalId()] = None

    # [Public]
    def get(self, id):
        """
            Returns group object by id provided. Id is an internal guid.
            If id does not exist in groupsmap, returns None.

            Args:
                id (str): a group's internal guid

            Returns:
                Group: object with id specified or None
        """
        return self._map[id] if self.has(id) else None

    # [Public]
    def guid(self, id):
        """
            Returns internal guid for id provided. Id is an external group id
            that comes from external system/service. It uses _guidmap to search
            for guid. Again, if two groups had the same external id, method
            may return different result for one of the groups.

            Args:
                id (str): external group's id

            Returns:
                str: internal group's guid if id is in _guidmap or None
        """
        if id is not None and id in self._guidmap:
            return self._guidmap[id]
        else:
             return None

    # [Public]
    def isEmpty(self):
        """
            Checks whether groupsmap contains any group or not. It checks
            only _map attribute. If there is no keys in _map, method returns
            True. Otherwise, method returns False.

            Returns:
                bool: indicator whether map is empty or not
        """
        return True if len(self._map.keys()) == 0 else False

    # [Public]
    def keys(self):
        """
            Returns keys as list from _map attribute. List would contain all
            the guids of all groups that are in _map and, possibly, in the
            system currently.

            Returns:
                list<str>: list of keys (guids) in _map attribute
        """
        return self._map.keys()

    # [Public]
    def values(self):
        """
            Returns values as list from _map attribute. List would contain all
            the Group objects that are in the groupsmap.

            Returns:
                list<Group>: list of groups that are in _map attribute
        """
        return self._map.values()

    # [Public]
    def unknownGroup(self):
        """
            Adds and returns unique unknown group instance. Unknown group is
            a  dummy group to consolidate all the results that have group
            attribute as None or unrelated to existing groups. It has specific
            id and there can be only one unknown group in groupsmap. When
            calling method, uknown group would be created and automatically
            added to groupsmap and then fetched from groupsmap.

            Returns:
                Group: unique unknown group
        """
        guid = "6120-31c2-4177-ad03-6d93a3a87976-unknown_id"
        if self.has(guid) is False:
            unknown = g.Group(guid, guid, "Unknown Group", "Unknown Group", None)
            self.assign(unknown)
            return unknown
        else:
            return self.get(guid)

    # [Public]
    def updateParentIdsToGuids(self):
        """
            Updates parent external id with internal guid for all the groups
            that are in _map dictionary. Parent id can be None.
        """
        for gid in self.keys():
            group = self.get(gid)
            group.updateParent(self.guid(group.getParent()))

    # [Public]
    def buildHierarchy(self):
        """
            Creates hierarchy from groups in place. Hierarchy is constructed in
            a way that there is no groups left, and all of them are nodes /
            roots of the tree.
            Each group with parent None is considered to be a root element.
            Every other element is checked upon having the root as parent, and
            children attribute is updated.

            Method deals with normal trees and also resolves situations when
            groups relate to themselves, or non-existing groups, or create a
            cycle, when the leaf the "root" references leaf.
            Hierarchy looks like this:
                [
                    element1, children: [
                        element2, children: [
                            element4, children: [],
                            element5, children: []
                        ],
                        element3, children: [
                            element6, children: []
                        ]
                    ],
                    element7, children: [
                        element8, children: []
                    ],
                    element9, children: []
                ]
        """
        # create dictionary {"parent_id":["child1", "child2",..]}
        pmap = {}   # map where all the children are mapped to their parent ids
        roots = []  # roots - elements with parent "None"
        for key in self.keys():
            group = self.get(key)
            pid = group.getParent() if self.has(group.getParent()) else None
            #if pid is None, we know that it is a root element
            if pid is None: roots.append(group)
            if pid not in pmap: pmap[pid] = []
            pmap[pid].append(group)
        for key in self.keys():
            self.get(key).assignChildren(pmap[key] if key in pmap else [])

        # collect all the valid tree elements
        #   and leave only ones that are cycles [potentially]
        valid = [] # array of valid elements
        for root in roots:
            self._collectTree(valid, root)
        cycles = list(set(self.values()) - set(valid))
        # check cycles and break them
        for cycle in cycles:
            self._traverseCycle(roots, cycle)
        #done, update groups
        self._map = {}
        for root in roots:
            self._map[root.getId()] = root

    # [Private]
    def _collectTree(self, array, root):
        """
            Recursively checks the element's children and collect them in
            list provided, therefore, there is a list that contains elements
            encountered. This method is used to exclude elements that have been
            scanned and used from general groupsmap in "buildHierarchy" method.

            Args:
                array (list<Group>): list to collect scanned elements
                root (Group): element to scan and retrieve children
        """
        if type(array) is not ListType:
            raise c.CheckError("<type 'list'>", str(type(array)))
        if type(root) is not g.Group:
            raise c.CheckError("<type 'Group'>", str(type(root)))

        if root is None or len(root.getChildren()) == 0:
            return False
        array.append(root)
        for child in root.getChildren():
            self._collectTree(array, child)

    # [Private]
    def _traverseCycle(self, collector, element, vlist={}):
        """
            Recursively checks for cycle. Element (Group instance) is checked
            and added to vlist as visited by creating pair {guid, flag}, where
            guid is internal group's id and flag is boolean value indicating
            that group has been added.

            When cycle is detected (element that currently searched is in
            vlist), element's parent is set to None, element is removed from
            parent's children list, thus, breaking cycle chain.

            Args:
                collector (list<Group>): list to collect groups with
                                            parent None
                element (Group): group object that currently being checked
                vlist (dict<str, bool>): dictionary to collect already
                                            traversed elements
        """
        if type(collector) is not ListType:
            raise c.CheckError("<type 'list'>", str(type(collector)))
        if type(element) is not g.Group:
            raise c.CheckError("<type 'Group'>", str(type(element)))

        if element is None or len(element.getChildren()) == 0: return False
        # check whether element is in vlist / is a cycle element
        if element.getId() in vlist:
            parent = self.get(element.getParent())
            parent.getChildren().remove(element)
            element.updateParent(None)
            collector.append(element)
            return False
        # add it to vlist, so we know that if next time we encounter it,
        #   it will be a cycle
        vlist[element.getId()] = True
        for child in element.getChildren():
            self._traverseCycle(collector, child, vlist)
