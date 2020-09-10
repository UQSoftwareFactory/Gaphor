"""Test issues where associations are copied and pasted, deleted, etc.

Scenario's:
* Class and association are pasted in a new diagram
* Class and association are pasted in a new diagram and original association is deleted
* Class and association are pasted in a new diagram and new association is deleted
* Association is pasted in a new diagram and reconnected to the class (same subject as original)
* Association is pasted and directly deleted
* Class and association are pasted in a new diagram and one end is connected to a different class

What's the behavior we're looking for?

* If an association has >1 presentations, it can only connect to those same types ()
* If an association has ==1 presentation, it can reconnect to another type, association is updated
"""

import pytest

from gaphor import UML
from gaphor.application import Session
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML import diagramitems
from gaphor.UML.modelfactory import set_navigability


@pytest.fixture
def session():
    session = Session()
    yield session
    session.shutdown()


@pytest.fixture
def element_factory(session):
    return session.get_service("element_factory")


@pytest.fixture
def copy(session):
    return session.get_service("copy")


@pytest.fixture
def diagram(element_factory):
    return element_factory.create(UML.Diagram)


@pytest.fixture
def class_and_association_with_copy(diagram, element_factory, copy):
    c = diagram.create(
        diagramitems.ClassItem, subject=element_factory.create(UML.Class)
    )

    a = diagram.create(diagramitems.AssociationItem)
    connect(a, a.handles()[0], c)
    connect(a, a.handles()[1], c)

    set_navigability(a.subject, a.subject.memberEnd[0], True)

    copy.copy({a, c})
    new_diagram = element_factory.create(UML.Diagram)
    pasted_items = copy.paste(new_diagram)

    aa = pasted_items.pop()
    if not isinstance(aa, diagramitems.AssociationItem):
        aa = pasted_items.pop()

    return c, a, aa


def test_delete_copied_associations(class_and_association_with_copy):

    c, a, aa = class_and_association_with_copy

    assert a.subject.memberEnd[0].type
    assert a.subject.memberEnd[1].type
    assert a.subject.memberEnd[0].type is c.subject
    assert a.subject.memberEnd[1].type is c.subject
    assert a.subject.memberEnd[0] is a.head_end.subject
    assert a.subject.memberEnd[1] is a.tail_end.subject
    assert a.subject.memberEnd[0] in a.subject.memberEnd[1].type.ownedAttribute

    # Delete the copy and all is fine

    aa.unlink()

    assert a.subject.memberEnd[0].type
    assert a.subject.memberEnd[1].type
    assert a.subject.memberEnd[0].type is c.subject
    assert a.subject.memberEnd[1].type is c.subject
    assert a.subject.memberEnd[0] is a.head_end.subject
    assert a.subject.memberEnd[1] is a.tail_end.subject
    assert a.subject.memberEnd[0] in a.subject.memberEnd[1].type.ownedAttribute


def test_delete_original_association(class_and_association_with_copy):

    c, a, aa = class_and_association_with_copy

    assert aa.subject.memberEnd[0].type
    assert aa.subject.memberEnd[1].type
    assert aa.subject.memberEnd[0].type is c.subject
    assert aa.subject.memberEnd[1].type is c.subject
    assert aa.subject.memberEnd[0] is aa.head_end.subject
    assert aa.subject.memberEnd[1] is aa.tail_end.subject
    assert aa.subject.memberEnd[0] in aa.subject.memberEnd[1].type.ownedAttribute

    # Now, when the original is deleted, the model is changed and made invalid

    a.unlink()

    assert aa.subject.memberEnd[0].type
    assert aa.subject.memberEnd[1].type
    assert aa.subject.memberEnd[0].type is c.subject
    assert aa.subject.memberEnd[1].type is c.subject
    assert aa.subject.memberEnd[0] is aa.head_end.subject
    assert aa.subject.memberEnd[1] is aa.tail_end.subject
    assert aa.subject.memberEnd[0] in aa.subject.memberEnd[1].type.ownedAttribute
