import itertools


class Suitor:
    def __init__(self, id, preference_list):
        self.preference_list = preference_list
        self.rejections = 0  # num rejections is also the index of the next option
        self.id = id

    def preference(self):
        return self.preference_list[self.rejections]

    def __eq__(self, other):
        return isinstance(other, Suitor) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return "Suitor({})".format(self.id)


class Suited:
    def __init__(self, id, preference_list):
        self.preference_list = preference_list
        self.held = None
        self.current_suitors = set()
        self.id = id

    def reject(self):
        if len(self.current_suitors) == 0:
            return set()

        if self.held is not None:
            self.current_suitors.add(self.held)

        self.held = min(self.current_suitors,
                        key=lambda suitor: self.preference_list.index(suitor.id))
        rejected = self.current_suitors - set([self.held])
        self.current_suitors = set()

        return rejected

    def __eq__(self, other):
        return isinstance(other, Suited) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return "Suited({})".format(self.id)


def stable_marriage(suitors, suiteds):
    """ Construct a stable marriage between Suitors and Suiteds.

    Arguments:
        suitors: a list of Suitor
        suiteds: a list of Suited, which deferred acceptance of Suitors.

    Returns:
        A dict {Suitor: Suited} matching Suitors to Suiteds.
    """
    unassigned = set(suitors)

    while len(unassigned) > 0:
        for suitor in unassigned:
            suiteds[suitor.preference()].current_suitors.add(suitor)
        unassigned = set()

        for suited in suiteds:
            unassigned |= suited.reject()

        for suitor in unassigned:
            suitor.rejections += 1

    return dict([(suited.held, suited) for suited in suiteds])


def verify_stable(suitors, suiteds, marriage):
    """ Check that the assignment of suitors to suited is a stable marriage.

    Arguments:
        suitors: a list of Suitors
        suiteds: a list of Suiteds
        marriage: a matching {Suitor: Suited}

    Returns:
        True if the marriage is stable, otherwise a tuple (False, (x, y))
        where x is a Suitor, y is a Suited, and (x, y) are a counterexample
        to the claim that the marriage is stable.
    """

    suited_to_suitor = dict((v, k) for (k, v) in marriage.items())

    def precedes(L, item1, item2): return L.index(item1) < L.index(item2)

    def suitor_prefers(suitor, suited):
        return precedes(suitor.preference_list, suited.id, marriage[suitor].id)

    def suited_prefers(suited, suitor):
        return precedes(suited.preference_list, suitor.id, suited_to_suitor[suited].id)

    for (suitor, suited) in itertools.product(suitors, suiteds):
        if (suited != marriage[suitor]
                and suitor_prefers(suitor, suited)
                and suited_prefers(suited, suitor)):
            return False, (suitor, suited)

    return True
